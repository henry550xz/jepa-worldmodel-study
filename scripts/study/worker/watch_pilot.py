#!/usr/bin/env python3
"""Controller observer only: compact retention/status; never launches experiments."""
import argparse
import json
import shlex
import subprocess
import time
from pathlib import Path

REPO=Path(__file__).resolve().parents[3]
STORE=Path('/mnt/research/jepa-worldmodel-study-storage')
SSH=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UpdateHostKeys=no',
     '-o','ConnectTimeout=15','-o','ServerAliveInterval=20','-o','ServerAliveCountMax=3']
REMOTE=r'''
import json,time,re
from pathlib import Path
r=Path('/root/autodl-tmp/robotics/jepa-worldmodel-study/runs')
q=r/'three-arm-pilot-queue'
state={'checked_at':time.time(),'stage':(q/'stage').read_text().strip() if (q/'stage').exists() else 'starting','runs':[]}
if (q/'queue.json').exists():state['worker_queue']=json.loads((q/'queue.json').read_text())
for f in r.glob('*/manifest.json'):
 m=json.loads(f.read_text())
 if m.get('phase')!='pilot':continue
 entry={'run_id':m['run_id'],'method':m['method'],'status':m['status'],'git_sha':m['git_sha'],'training_start':m.get('training_start'),'training_wall_seconds':m.get('training_wall_seconds')}
 log=f.parent/'train.log'
 if log.exists():
  with log.open('rb') as t:
   t.seek(max(0,log.stat().st_size-30000));tail=t.read().decode(errors='replace')
  matches=re.findall(r'MATCHED train epoch=(\d+) step=(\d+) batch=(\d+) seconds=([\d.]+)',tail)
  if matches:entry['progress']=matches[-1]
  entry['log_age_seconds']=time.time()-log.stat().st_mtime
 results=list(f.parent.glob('common-pilot-*/metrics.json'))
 if results:entry['evaluation']=json.loads(max(results,key=lambda x:x.stat().st_mtime).read_text()).get('status')
 state['runs'].append(entry)
print(json.dumps(state))
'''


def main():
    p=argparse.ArgumentParser();p.add_argument('alias');a=p.parse_args()
    while True:
        subprocess.run(['mountpoint','-q','/mnt/research'],check=True)
        state=json.loads(subprocess.check_output([*SSH,a.alias,'/root/miniconda3/bin/python -c '+shlex.quote(REMOTE)],text=True,timeout=45))
        for run in state['runs']:
            subprocess.run(['bash',str(REPO/'scripts/study/worker/sync_compact_results_back.sh'),a.alias,run['run_id']],check=True,timeout=180)
        path=STORE/'runs/pilot-queue.json';temp=path.with_suffix('.tmp');temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(path)
        print(json.dumps(state),flush=True)
        if state['stage']=='complete':return
        if state['stage']=='failed' or any(r['status'].startswith('failed') or r.get('evaluation')=='failed' for r in state['runs']):raise SystemExit(78)
        time.sleep(60)

if __name__=='__main__':main()
