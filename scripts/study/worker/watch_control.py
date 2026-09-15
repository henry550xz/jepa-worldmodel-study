#!/usr/bin/env python3
"""Observe an inference-control process and retain artifacts; never launch jobs."""
import argparse,json,re,shlex,subprocess,time,hashlib
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('alias');p.add_argument('folder');p.add_argument('pid',type=int);a=p.parse_args()
 if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',a.folder):raise ValueError('invalid folder')
 ssh=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UpdateHostKeys=no','-o','ConnectTimeout=15','-o','ServerAliveInterval=20','-o','ServerAliveCountMax=3']
 remote='/root/autodl-tmp/robotics/jepa-worldmodel-study/artifacts/'+a.folder;dest=Path('/mnt/research/jepa-worldmodel-study-storage/artifacts')/a.folder
 while True:
  subprocess.run(['mountpoint','-q','/mnt/research'],check=True);dest.mkdir(exist_ok=True)
  code=f"import json,pathlib; d=json.loads(pathlib.Path({remote!r}+'/state.json').read_text()); p=pathlib.Path('/proc/{a.pid}/cmdline'); d['observed_process_alive']=p.exists() and b'study.reencode_control' in p.read_bytes(); print(json.dumps(d))"
  state=json.loads(subprocess.check_output([*ssh,a.alias,'/root/miniconda3/bin/python -c '+shlex.quote(code)],text=True,timeout=45))
  subprocess.run(['rsync','-az','--partial','--safe-links','-e',' '.join(ssh),'--include=*.json','--include=*.npz','--exclude=*',a.alias+':'+remote+'/',str(dest)+'/'],check=True,timeout=180)
  print(json.dumps(state),flush=True)
  if state['status']=='complete':
   records=[{'name:f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for f in dest.iterdir() if f.is_file() and f.name!='artifact-inventory.json'];(dest/'artifact-inventory.json').write_text(json.dumps(records,indent=2)+'\n');return
  if state['status']=='failed' or not state['observed_process_alive']:raise SystemExit(78)
  time.sleep(60)
if __name__=='__main__':main()
