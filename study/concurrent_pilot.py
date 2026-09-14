"""Authorized three-way training with sequential common evaluation; fail closed."""
import argparse
import fcntl
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from study.run import worker_root_checked
from study.manifests import provenance


def write(path,state):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(path)


def main():
    p=argparse.ArgumentParser();p.add_argument('--authorized-full-pilot',action='store_true');a=p.parse_args()
    if not a.authorized_full_pilot:raise SystemExit('Explicit full-pilot authorization required')
    root=worker_root_checked('/root/autodl-tmp/robotics/jepa-worldmodel-study');repo=Path(__file__).resolve().parents[1]
    info=provenance(repo);lock=(root/'runs/three-arm-pilot.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    # Same guard as the prepared sequential launcher, so only one mode can run.
    folder=root/'runs/three-arm-pilot-queue';folder.mkdir(exist_ok=False)
    state={'mode':'three-way','status':'running','stage':'training',**info,'started_at':time.time(),'runs':{},'pids':{}}
    procs={};logs=[]
    try:
        for method in ['pixel','gaussian','sparse']:
            log=(folder/(method+'-launch.log')).open('w');logs.append(log)
            proc=subprocess.Popen([sys.executable,'-m','study.run','--method',method,'--phase','pilot','--seed','0',
                '--dataset-version','442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08'],
                cwd=repo,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            procs[method]=proc;state['pids'][method]=proc.pid
        while True:
            for f in (root/'runs').glob('*/manifest.json'):
                m=json.loads(f.read_text())
                if m.get('phase')=='pilot' and m['git_sha']==info['git_sha']:
                    old=state['runs'].get(m['method'])
                    if old and old!=m['run_id']:raise RuntimeError('duplicate pilot arm detected')
                    state['runs'][m['method']]=m['run_id']
            state['updated_at']=time.time();write(folder/'queue.json',state)
            (folder/'stage').write_text('concurrent training\n')
            if any(p.poll() not in (None,0) for p in procs.values()):raise RuntimeError('pilot training failed; all remaining training stopped')
            if all(p.poll()==0 for p in procs.values()):break
            time.sleep(10)
        if len(state['runs'])!=3:raise RuntimeError('missing arm manifest')
        # No planning contention with training: all models finish before evaluation.
        for method in ['pixel','gaussian','sparse']:
            run=state['runs'][method];state.update(stage='evaluation',active_method=method,updated_at=time.time())
            write(folder/'queue.json',state);(folder/'stage').write_text(method+' evaluation\n')
            with (folder/(method+'-evaluation.log')).open('w') as log:
                subprocess.run([sys.executable,'-m','study.evaluate_common',run,'--profile','pilot'],
                    cwd=repo,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,check=True)
        state.update(status='complete',stage='complete',ended_at=time.time());(folder/'stage').write_text('complete\n')
    except BaseException as e:
        state.update(status='failed',error_type=type(e).__name__,error=str(e),ended_at=time.time())
        (folder/'stage').write_text('failed\n')
        raise
    finally:
        for p in procs.values():
            if p.poll() is None:os.killpg(p.pid,signal.SIGTERM)
        for p in procs.values():
            try:p.wait(timeout=15)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
        write(folder/'queue.json',state)
        for log in logs:log.close()

if __name__=='__main__':main()
