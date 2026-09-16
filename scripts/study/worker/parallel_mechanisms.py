"""Two-slot coordinator adopting the existing immutable Pixel training process.

All scientific subprocesses use original snapshot/configuration. Evaluations are
serialized after each pair. Failure pauses surviving training without discarding
its in-memory state. No automatic scientific retries or checkpoint deletions.
"""
import os,sys,time,json,subprocess,signal,fcntl,shutil,math
from pathlib import Path
ROOT=Path('/root/autodl-tmp/robotics/jepa-worldmodel-study')
QUEUE='mechanism-seed0-20260915T2225Z'
SHA='98816c638b4c2329079feffafde4090c0614cf3a'
SNAP=ROOT/'code'/SHA
ARMS=['pixel','pixel_rollout','pixel_consistency','gaussian']

def write(path,data):
 temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(path)

def main():
 folder=ROOT/'runs'/QUEUE;state_path=folder/'state.json'
 lock=(ROOT/'runs/mechanism-full.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 state=json.loads(state_path.read_text());assert state['sha']==SHA and state['stage']=='training' and state['active_arm']=='pixel'
 assert not (folder/'parallel-adopted.json').exists()
 pixel_pid=489052
 assert b'study.instrument' in Path(f'/proc/{pixel_pid}/cmdline').read_bytes()
 template=json.loads((ROOT/'runs'/state['runs']['pixel']/'manifest.json').read_text())
 write(folder/'parallel-adopted.json',{'pixel_pid':pixel_pid,'adopted_at':time.time(),'coordinator_sha':Path(__file__).resolve().parents[3].name,'scientific_sha':SHA})
 state.update(scheduling='two training slots; serialized pair evaluation',coordinator_pid=os.getpid(),active_training=['pixel'],completed=[])
 env=dict(os.environ,DATASET_DIR=str(ROOT/'datasets'),WANDB_MODE='offline',WANDB_CACHE_DIR=str(ROOT/'caches/wandb'),TORCH_HOME=str(ROOT/'caches/torch'),TMPDIR=str(ROOT/'caches/tmp'),MPLCONFIGDIR=str(ROOT/'caches/matplotlib'),XDG_CACHE_HOME=str(ROOT/'caches/xdg'),PYTHONDONTWRITEBYTECODE='1',SDL_VIDEODRIVER='dummy',TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD='1',WORLD_SIZE='1',RANK='0',LOCAL_RANK='0',MASTER_ADDR='127.0.0.1')
 active={'pixel':pixel_pid};children={}
 def launch(arm):
  if shutil.disk_usage(ROOT).free<4*1024**3:raise RuntimeError('data disk headroom below4GiB')
  rid=QUEUE+'-'+arm;r=ROOT/'runs'/rid;r.mkdir(exist_ok=False)
  ov=[('hydra.run.dir='+str(ROOT/'checkpoints/outputs'/rid)) if x.startswith('hydra.run.dir=') else ('+model.mechanism='+arm) if x.startswith('+model.mechanism=') else x for x in template['overrides']]
  m=dict(template,run_id=rid,method='gaussian' if arm=='gaussian' else 'pixel',mechanism=arm,overrides=ov,training_start=time.time(),status='running',scheduling='two-slot concurrent',coordinator_sha=Path(__file__).resolve().parents[3].name)
  write(r/'manifest.json',m);e=dict(env,MASTER_PORT=str(29710+ARMS.index(arm)),WANDB_DIR=str(r))
  with (r/'resolved-config.yaml').open('w') as conf,(r/'resolve.log').open('w') as log:subprocess.run([sys.executable,'train.py',*ov,'--cfg','job','--resolve'],cwd=SNAP,env=e,stdout=conf,stderr=log,check=True)
  log=(r/'train.log').open('w');p=subprocess.Popen([sys.executable,'-u','-m','study.instrument','--telemetry',str(r/'telemetry.json'),'--matched','--',*ov],cwd=SNAP,env=e,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  children[arm]=p;active[arm]=p.pid;state['runs'][arm]=rid;state['active_training']=list(active);write(state_path,state)
 def verify(arm):
  rid=state['runs'][arm];r=ROOT/'runs'/rid;t=json.loads((r/'telemetry.json').read_text());losses=t['train_losses']
  assert len(losses)==104430 and all(math.isfinite(x) for x in losses), 'incomplete/nonfinite training'
  cp=ROOT/'checkpoints/outputs'/rid/'checkpoints/model_latest.pth';assert cp.exists()
  m=json.loads((r/'manifest.json').read_text());m.update(status='training_complete',checkpoint_path=str(cp),checkpoint_bytes=cp.stat().st_size,training_end=time.time());write(r/'manifest.json',m)
  (r/'resolved-config.yaml').write_bytes((cp.parents[1]/'hydra.yaml').read_bytes())
 try:
  for pair in [('pixel','pixel_rollout'),('pixel_consistency','gaussian')]:
   state.update(stage='training',active_arm='+'.join(pair));write(state_path,state)
   for arm in pair:
    if arm not in active:launch(arm)
   while active:
    for arm,pid in list(active.items()):
     if arm in children:
      ret=children[arm].poll()
      if ret is None:continue
      if ret!=0:raise RuntimeError(f'{arm} training exited{ret}')
     elif Path(f'/proc/{pid}').exists():continue
     verify(arm);del active[arm];state['active_training']=list(active);write(state_path,state)
    time.sleep(15)
   for arm in pair:
    state.update(stage='evaluation',active_arm=arm);write(state_path,state)
    rid=state['runs'][arm];r=ROOT/'runs'/rid
    with (r/'evaluation.log').open('w') as log:subprocess.run([sys.executable,'-u','-m','study.mechanism_evaluate',rid,'--profile','pilot'],cwd=SNAP,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    metrics=json.loads((r/('common-pilot-'+SHA[:12])/'metrics.json').read_text());assert metrics['status']=='passed' and metrics.get('latent_closure')
    state['completed'].append(rid);write(state_path,state)
  state.update(status='complete',stage='complete',active_arm=None)
 except BaseException as exc:
  for pid in active.values():
   try:os.kill(pid,signal.SIGSTOP)
   except ProcessLookupError:pass
  state.update(status='failed',error=str(exc),paused_training=active);raise
 finally:write(state_path,state)
if __name__=='__main__':main()
