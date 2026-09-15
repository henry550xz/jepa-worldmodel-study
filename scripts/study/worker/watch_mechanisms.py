"""Controller retention observer; never launches scientific stages."""
import argparse,json,subprocess,time,shlex,hashlib
from pathlib import Path
SSH=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UpdateHostKeys=no','-o','ConnectTimeout=15']
ROOT='/root/autodl-tmp/robotics/jepa-worldmodel-study'
REPO=Path(__file__).resolve().parents[3]
STORE=Path('/mnt/research/jepa-worldmodel-study-storage')

def main():
 p=argparse.ArgumentParser();p.add_argument('alias');p.add_argument('queue');a=p.parse_args()
 if not all(c.isalnum() or c in '-_' for c in a.queue):raise ValueError('unsafe queue')
 while True:
  try:
   subprocess.run(['mountpoint','-q','/mnt/research'],check=True)
   state=json.loads(subprocess.check_output([*SSH,a.alias,'cat '+ROOT+'/runs/'+a.queue+'/state.json'],text=True,timeout=30))
   folder=STORE/'runs'/a.queue;folder.mkdir(exist_ok=True);(folder/'state.json').write_text(json.dumps(state,indent=2)+'\n')
   for rid in state['runs'].values():
    dest=STORE/'runs'/rid;dest.mkdir(exist_ok=True)
    subprocess.run(['rsync','-az','--partial','--safe-links','-e',shlex.join(SSH),'--exclude=.env*','--exclude=wandb/',a.alias+':'+ROOT+'/runs/'+rid+'/',str(dest)+'/'],check=True,timeout=180)
    manifest=json.loads((dest/'manifest.json').read_text())
    if manifest['status']=='training_complete' and not (dest/'checkpoint-retention.json').exists():
     cp=manifest['checkpoint_path'];target=STORE/'checkpoints'/rid;target.mkdir(exist_ok=True)
     subprocess.run(['rsync','-az','--partial','-e',shlex.join(SSH),a.alias+':'+cp,str(target)+'/'],check=True,timeout=1800)
     remote=subprocess.check_output([*SSH,a.alias,'sha256sum '+shlex.quote(cp)],text=True,timeout=180).split()[0]
     h=hashlib.sha256()
     with (target/'model_latest.pth').open('rb') as f:
      for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
     if h.hexdigest()!=remote:raise RuntimeError('checkpoint hash mismatch')
     (dest/'checkpoint-retention.json').write_text(json.dumps({'sha256':remote,'path':str(target/'model_latest.pth')},indent=2))
   print(json.dumps(state),flush=True)
   if state['status'] in ('complete','failed'):return
  except Exception as exc:print('OBSERVER_ERROR',str(exc),flush=True)
  time.sleep(90)
if __name__=='__main__':main()
