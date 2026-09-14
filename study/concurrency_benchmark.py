"""Disposable timed benchmark of the frozen pilot; never runs evaluation/checkpoints."""
import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT=Path('/root/autodl-tmp/robotics/jepa-worldmodel-study')
DATA_SHA='442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08'
METHODS=['pixel','gaussian','sparse']


def write(path,data):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');temp.replace(path)


def child(args):
    from study.run import worker_root_checked,training_overrides
    from study.manifests import provenance,create_manifest,write_manifest,utcnow
    root=worker_root_checked(str(ROOT));repo=Path(__file__).resolve().parents[1]
    info=provenance(repo)
    os.environ.update(DATASET_DIR=str(root/'datasets'),WANDB_MODE='offline',
        WANDB_CACHE_DIR=str(root/'caches/wandb'),TORCH_HOME=str(root/'caches/torch'),
        TMPDIR=str(root/'caches/tmp'),MPLCONFIGDIR=str(root/'caches/matplotlib'),
        XDG_CACHE_HOME=str(root/'caches/xdg'),PYTHONDONTWRITEBYTECODE='1',
        SDL_VIDEODRIVER='dummy',TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD='1',CUDA_VISIBLE_DEVICES='0',
        WORLD_SIZE='1',RANK='0',LOCAL_RANK='0',MASTER_ADDR='127.0.0.1')
    with socket.socket() as sock:
        sock.bind(('',0));os.environ['MASTER_PORT']=str(sock.getsockname()[1])
    folder,m=create_manifest(root/'runs',provenance_info=info,method=args.method,seed=0,
        dataset_path=root/'datasets/pusht_noise',dataset_version=DATA_SHA,resolved_config=None,
        planning_settings={},evaluation_settings={'status':'not_run','reason':'disposable throughput benchmark only'})
    os.environ['WANDB_DIR']=str(folder)
    m.update(phase='concurrency_benchmark',status='initializing',cohort=args.group,
             warmup_updates=args.warmup,measurement_seconds=args.seconds,pid=os.getpid())
    group=Path(args.group);write(group/(args.method+'-run.json'),{'run_id':m['run_id'],'manifest':str(folder/'manifest.json'),'pid':os.getpid()})
    import torch
    import train
    from study.matched_training import install
    stats={};install(train,stats,0)
    measured={};original=train.Trainer.__init__
    class TimedLoader:
        def __init__(self,loader):self.loader=loader
        def __iter__(self):
            loader=iter(self.loader);n=0;waits=[];begin=None
            while True:
                if n==args.warmup:
                    torch.cuda.synchronize()
                    write(group/(args.method+'.ready'),{'pid':os.getpid(),'time':time.time()})
                    deadline=time.monotonic()+180
                    while not (group/'start.json').exists():
                        if time.monotonic()>deadline:raise RuntimeError('benchmark barrier timeout')
                        time.sleep(.02)
                    start_at=json.loads((group/'start.json').read_text())['start_at']
                    while time.time()<start_at:time.sleep(.005)
                    begin=time.monotonic();measured['start_at']=time.time()
                if begin is not None and time.monotonic()-begin>=args.seconds:break
                t=time.monotonic();batch=next(loader);delay=time.monotonic()-t
                if begin is not None:waits.append(delay)
                yield batch
                n+=1
            torch.cuda.synchronize();duration=time.monotonic()-begin
            measured.update(end_at=time.time(),seconds=duration,updates=n-args.warmup,
                windows=(n-args.warmup)*32,windows_per_second=(n-args.warmup)*32/duration,
                loader_wait_seconds=sum(waits),loader_wait_fraction=sum(waits)/duration,
                dataset_windows=len(self.loader.dataset),loader_batches=len(self.loader),
                allocated_peak_bytes=torch.cuda.max_memory_allocated(),
                reserved_peak_bytes=torch.cuda.max_memory_reserved(),
                allocation_retries=torch.cuda.memory_stats().get('num_alloc_retries',0),
                allocator_ooms=torch.cuda.memory_stats().get('num_ooms',0))
    def initialize(self,cfg):
        original(self,cfg);self.dataloaders['train']=TimedLoader(self.dataloaders['train'])
    train.Trainer.__init__=initialize
    train.Trainer.run=lambda self:self.train()  # Explicitly no validation, plots or checkpoint save.
    overrides=training_overrides(args.method,'pilot',0,root,m['run_id'])
    m.update(command_overrides=overrides,status='running',training_start=utcnow())
    write_manifest(folder,m)
    sys.argv=['train.py','--config-path',str(repo/'conf'),*overrides]
    torch.cuda.reset_peak_memory_stats()
    try:
        train.main()
        if measured.get('updates',0)<=0:raise RuntimeError('benchmark performed no measured updates')
        m.update(status='benchmark_complete',measurement=measured)
    except BaseException as e:
        m.update(status='failed',error_type=type(e).__name__,error=str(e));raise
    finally:
        m['training_end']=utcnow();m['telemetry']=stats
        write_manifest(folder,m);write(group/(args.method+'-result.json'),m)
        import wandb
        wandb.finish()


def suite(args):
    import psutil
    from study.run import worker_root_checked
    from study.manifests import provenance,utcnow
    from study.partitions import PARTITIONS
    import hashlib
    worker_root_checked(str(ROOT));repo=Path(__file__).resolve().parents[1];info=provenance(repo)
    folder=ROOT/'runs'/('concurrency-'+time.strftime('%Y%m%dT%H%M%S',time.gmtime()))
    folder.mkdir(exist_ok=False)
    state={'status':'running','folder':str(folder),**info,'seconds':args.seconds,'warmup':args.warmup,
           'partitions_sha256':hashlib.sha256(PARTITIONS.read_bytes()).hexdigest(),'groups':{},
           'cpu_affinity_count':len(os.sched_getaffinity(0)),'host_logical_cpus':psutil.cpu_count()}
    write(ROOT/'runs/concurrency-benchmark-latest.json',state)
    try:
        for name,methods in [('solo-'+m,[m]) for m in METHODS]+[('three-way',METHODS)]:
            group=folder/name;group.mkdir();state['active_group']=name;write(folder/'status.json',state)
            procs=[];logs=[];samples=[];cpu_max={};io_max={}
            cpu_start=psutil.cpu_times();start=time.time()
            try:
                for method in methods:
                    log=(group/(method+'.log')).open('w');logs.append(log)
                    p=subprocess.Popen([sys.executable,'-m','study.concurrency_benchmark','--child','--method',method,
                        '--group',str(group),'--seconds',str(args.seconds),'--warmup',str(args.warmup)],
                        cwd=repo,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                    procs.append(p)
                while any(p.poll() is None for p in procs):
                    if any(p.poll() not in (None,0) for p in procs):raise RuntimeError('benchmark child failed; inspect group logs')
                    if time.time()-start>420:raise RuntimeError('bounded benchmark group exceeded seven minutes')
                    if not (group/'start.json').exists() and all((group/(m+'.ready')).exists() for m in methods):
                        write(group/'start.json',{'start_at':time.time()+2})
                    sample={'time':time.time()}
                    try:
                        row=subprocess.check_output(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,memory.total',
                            '--format=csv,noheader,nounits'],text=True,timeout=5).strip().split(',')
                        sample.update(gpu_percent=float(row[0]),driver_mib=float(row[1]),total_mib=float(row[2]))
                    except Exception:pass
                    active=[]
                    for p in procs:
                        try:active.extend([psutil.Process(p.pid),*psutil.Process(p.pid).children(recursive=True)])
                        except psutil.Error:pass
                    cpu=0;read_bytes=0;read_chars=0
                    for p in active:
                        try:
                            c=p.cpu_times();io=p.io_counters();key=str(p.pid)
                            cpu_max[key]=max(cpu_max.get(key,0),c.user+c.system)
                            io_max[key]=[max(io_max.get(key,[0,0])[0],io.read_bytes),max(io_max.get(key,[0,0])[1],io.read_chars)]
                        except psutil.Error:pass
                    c=psutil.cpu_times();sample.update(process_cpu_seconds=sum(cpu_max.values()),
                        read_bytes=sum(v[0] for v in io_max.values()),read_chars=sum(v[1] for v in io_max.values()),
                        host_iowait_seconds=getattr(c,'iowait',0),host_idle_seconds=c.idle,host_cpu_seconds=sum(c),
                        processes=len(active))
                    samples.append(sample)
                    with (group/'resources.jsonl').open('a') as f:f.write(json.dumps(sample)+'\n')
                    time.sleep(1)
                if any(p.returncode!=0 for p in procs):raise RuntimeError('benchmark child nonzero exit')
                results={m:json.loads((group/(m+'-result.json')).read_text()) for m in methods}
                if any(m['status']!='benchmark_complete' for m in results.values()):raise RuntimeError('incomplete benchmark')
                lo=min(m['measurement']['start_at'] for m in results.values());hi=max(m['measurement']['end_at'] for m in results.values())
                active_samples=[s for s in samples if lo<=s['time']<=hi]
                first,last=active_samples[0],active_samples[-1];dt=last['time']-first['time']
                cpu_delta=last['host_cpu_seconds']-first['host_cpu_seconds']
                summary={'results':results,'aggregate_windows_per_second':sum(m['measurement']['windows'] for m in results.values())/(hi-lo),
                    'driver_peak_mib':max(s.get('driver_mib',0) for s in samples),
                    'mean_gpu_percent':sum(s.get('gpu_percent',0) for s in active_samples)/len(active_samples),
                    'process_cpu_cores':(last['process_cpu_seconds']-first['process_cpu_seconds'])/dt,
                    'host_cpu_busy_percent':100*(1-(last['host_idle_seconds']-first['host_idle_seconds'])/cpu_delta),
                    'host_iowait_percent':100*(last['host_iowait_seconds']-first['host_iowait_seconds'])/cpu_delta,
                    'read_bytes_per_second':(last['read_bytes']-first['read_bytes'])/dt,
                    'read_chars_per_second':(last['read_chars']-first['read_chars'])/dt}
                state['groups'][name]=summary;write(folder/'status.json',state)
                print(json.dumps({'group':name,'aggregate_windows_per_second':summary['aggregate_windows_per_second'],'driver_peak_mib':summary['driver_peak_mib']}),flush=True)
            finally:
                for p in procs:
                    if p.poll() is None:os.killpg(p.pid,signal.SIGTERM)
                for p in procs:
                    try:p.wait(timeout=15)
                    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
                for log in logs:log.close()
        rates=[state['groups']['solo-'+m]['results'][m]['measurement']['windows_per_second'] for m in METHODS]
        seq=3/sum(1/r for r in rates);con=state['groups']['three-way']['aggregate_windows_per_second']
        state.update(status='complete',sequential_equivalent_windows_per_second=seq,concurrent_gain=con/seq-1,ended_at=utcnow())
    except BaseException as e:
        state.update(status='failed',error_type=type(e).__name__,error=str(e));raise
    finally:
        write(folder/'status.json',state);write(ROOT/'runs/concurrency-benchmark-latest.json',state)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--child',action='store_true');p.add_argument('--method',choices=METHODS)
    p.add_argument('--group');p.add_argument('--seconds',type=int,default=60);p.add_argument('--warmup',type=int,default=20)
    a=p.parse_args()
    if not 10<=a.seconds<=120 or not 2<=a.warmup<=50:raise ValueError('bounded benchmark interval required')
    if a.child:child(a)
    else:suite(a)
