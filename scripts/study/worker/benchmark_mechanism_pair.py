"""Bounded scheduling benchmark; existing scientific process is resumed in finally."""
import os,signal,time,json,re,subprocess,sys
from pathlib import Path
ROOT=Path('/root/autodl-tmp/robotics/jepa-worldmodel-study')
PID=489052
PIXEL=ROOT/'runs/mechanism-seed0-20260915T2225Z-pixel/train.log'
SNAPSHOT=ROOT/'code/98816c638b4c2329079feffafde4090c0614cf3a'

def step(path):
 if not path.exists():return 0
 with path.open('rb') as f:
  f.seek(max(0,path.stat().st_size-8192));s=f.read().decode(errors='replace')
 m=re.findall(r'MATCHED train epoch=(\d+) step=(\d+)',s)
 return (int(m[-1][0])-1)*52215+int(m[-1][1]) if m else 0

def main():
 out=ROOT/'runs/mechanism-pair-benchmark-20260916';out.mkdir(exist_ok=False)
 assert b'study.instrument' in Path(f'/proc/{PID}/cmdline').read_bytes()
 m=json.loads((ROOT/'runs/mechanism-pixel_rollout-s0-5a5b5132ca75/manifest.json').read_text())
 ov=[v if not v.startswith('hydra.run.dir=') else 'hydra.run.dir='+str(ROOT/'checkpoints/outputs'/out.name) for v in m['overrides']]
 env=dict(os.environ,DATASET_DIR=str(ROOT/'datasets'),WANDB_MODE='offline',WANDB_DIR=str(out),TMPDIR=str(ROOT/'caches/tmp'),XDG_CACHE_HOME=str(ROOT/'caches/xdg'),MPLCONFIGDIR=str(ROOT/'caches/matplotlib'),TORCH_HOME=str(ROOT/'caches/torch'),PYTHONDONTWRITEBYTECODE='1',TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD='1',MASTER_ADDR='127.0.0.1',MASTER_PORT='29619',WORLD_SIZE='1',RANK='0',LOCAL_RANK='0',SDL_VIDEODRIVER='dummy')
 result={'scientific_sha':SNAPSHOT.name,'benchmark_sha':Path(__file__).resolve().parents[3].name,'pixel_pid':PID,'measurements':[]}
 child=None
 def measure(label,seconds=40):
  start=time.monotonic();p0=step(PIXEL);r0=step(out/'train.log');samples=[]
  while time.monotonic()-start<seconds:
   if child and child.poll() is not None:raise RuntimeError('benchmark process ended early')
   samples.append(subprocess.check_output(['nvidia-smi','--query-gpu=utilization.gpu,memory.used','--format=csv,noheader,nounits'],text=True).strip())
   time.sleep(5)
  duration=time.monotonic()-start
  row={'stage':label,'seconds':duration,'pixel_updates':step(PIXEL)-p0,'rollout_updates':step(out/'train.log')-r0,'gpu_samples_util_percent_memory_MiB':samples}
  result['measurements'].append(row);(out/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps(row),flush=True)
 try:
  measure('pixel_alone')
  os.kill(PID,signal.SIGSTOP)
  log=(out/'train.log').open('w')
  child=subprocess.Popen([sys.executable,'-u','-m','study.instrument','--telemetry',str(out/'telemetry.json'),'--smoke-batches','2000','--matched','--',*ov],cwd=SNAPSHOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  deadline=time.monotonic()+120
  while step(out/'train.log')<20:
   if child.poll() is not None or time.monotonic()>deadline:raise RuntimeError('benchmark warmup failed/timed out')
   time.sleep(2)
  measure('rollout_alone_pixel_paused')
  os.kill(PID,signal.SIGCONT);time.sleep(10)
  measure('pixel_plus_rollout',60)
  result['status']='passed'
 except BaseException as exc:
  result.update(status='failed',error=str(exc));raise
 finally:
  os.kill(PID,signal.SIGCONT)
  if child and child.poll() is None:
   os.killpg(child.pid,signal.SIGINT)
   try:child.wait(timeout=20)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=10)
  (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
