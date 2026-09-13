#!/usr/bin/env python3
"""Controller-only sequential watcher for the two explicitly authorized reproductions.

No science code is changed. Uses immutable worker snapshots and retrieves evidence.
Stops on any failed run. Never deletes remote/local results or logs environments.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

SSH=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UpdateHostKeys=no',
     '-o','ConnectTimeout=20','-o','ServerAliveInterval=30','-o','ServerAliveCountMax=4']
ROOT='/root/autodl-tmp/robotics/jepa-worldmodel-study'
STORE=Path('/mnt/research/jepa-worldmodel-study-storage')
REPO=Path(__file__).resolve().parents[3]


def remote(alias, command):
    return subprocess.check_output([*SSH,alias,command],text=True,timeout=45)


def manifest(alias, run_id):
    return json.loads(remote(alias,f'cat {ROOT}/runs/{run_id}/manifest.json'))


def record(path, state):
    subprocess.run(['mountpoint','-q','/mnt/research'],check=True)
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(path)
    status=REPO/'docs/CURRENT_PROJECT_STATUS.md'
    marker='\n## Live reproduction monitor\n'
    original=status.read_text().split(marker)[0]
    status.write_text(original+marker+'\nUpdated automatically from the controller monitor; no scientific result is inferred from an active run.\n\n```json\n'+json.dumps(state,indent=2)+'\n```\n')


def sync(alias,run_id):
    subprocess.run(['bash',str(REPO/'scripts/study/worker/sync_compact_results_back.sh'),alias,run_id],check=True,timeout=180)


def wait(alias,run_id,stage,state,path):
    while True:
        m=manifest(alias,run_id)
        current=m['status'] if stage=='training' else m['evaluation_settings']['status']
        state.update(active_run=run_id,stage=stage,status=current,updated_at=time.time())
        record(path,state)
        sync(alias,run_id)
        print(json.dumps({'run_id':run_id,'stage':stage,'status':current}),flush=True)
        done='training_complete' if stage=='training' else 'complete'
        if current==done:return m
        if current.startswith('failed'):raise RuntimeError(f'{run_id} {stage} failed')
        time.sleep(60)


def launch_plan(alias,sha,run_id):
    command=(f'cd {ROOT}/code/{sha} && '
        f'nohup {ROOT}/envs/lpwm-5090/bin/python -m study.plan_official {run_id} '
        f'> {ROOT}/runs/{run_id}/planning-launch.log 2>&1 < /dev/null &')
    remote(alias,command)
    # Allow imports/provenance checks to transition the existing evaluation record.
    for _ in range(20):
        m=manifest(alias,run_id)
        if m['evaluation_settings']['status']!='not_run':return
        time.sleep(3)
    raise RuntimeError('planning failed to start; inspect planning-launch.log')


def retain_checkpoint(alias,run_id,m):
    dest=STORE/'checkpoints'/run_id;dest.mkdir(parents=True,exist_ok=True)
    source=f'{ROOT}/checkpoints/outputs/{run_id}/checkpoints/model_latest.pth'
    expected=remote(alias,f'sha256sum {source}').split()[0]
    subprocess.run(['rsync','-az','--partial','-e',' '.join(SSH),f'{alias}:{source}',str(dest/'model_latest.pth')],check=True)
    h=hashlib.sha256()
    with (dest/'model_latest.pth').open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    if h.hexdigest()!=expected:raise RuntimeError('checkpoint transfer hash mismatch')
    (dest/'SHA256.json').write_text(json.dumps({'sha256':expected,'source':source,'git_sha':m['git_sha']},indent=2)+'\n')
    # Matching resolved config is retained alongside the module checkpoint.
    (dest/'resolved-config.yaml').write_bytes((STORE/'runs'/run_id/'resolved-config.yaml').read_bytes())


def main():
    p=argparse.ArgumentParser();p.add_argument('alias');p.add_argument('sha');p.add_argument('gaussian_run');p.add_argument('--resume',action='store_true')
    a=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',a.alias) or not re.fullmatch(r'[0-9a-f]{40}',a.sha):raise ValueError('invalid alias/SHA')
    if not re.fullmatch(r'gaussian-[A-Za-z0-9_-]+',a.gaussian_run):raise ValueError('invalid Gaussian run')
    subprocess.run(['mountpoint','-q','/mnt/research'],check=True)
    path=STORE/'runs'/'reproduction-queue.json'
    if path.exists() and not a.resume:raise RuntimeError('queue record already exists; use --resume after inspection')
    state=json.loads(path.read_text()) if path.exists() else {'source_sha':a.sha,'alias':a.alias,'gaussian_run':a.gaussian_run,'status':'starting'}
    if state['source_sha']!=a.sha or state['gaussian_run']!=a.gaussian_run or state['alias']!=a.alias:raise ValueError('resume identity mismatch')
    if state['status']=='complete':return
    record(path,state)
    try:
        m=manifest(a.alias,a.gaussian_run)
        if m['git_sha']!=a.sha or m['phase']!='reproduction':raise ValueError('wrong starting run')
        m=wait(a.alias,a.gaussian_run,'training',state,path)
        if m['evaluation_settings']['status']=='not_run':launch_plan(a.alias,a.sha,a.gaussian_run)
        m=wait(a.alias,a.gaussian_run,'evaluation',state,path)
        retain_checkpoint(a.alias,a.gaussian_run,m)
        # Only launch sparse after Gaussian training AND official planning succeed.
        command=(f'cd {ROOT}/code/{a.sha} && nohup {ROOT}/envs/lpwm-5090/bin/python -m study.run '
            f'--method sparse --phase reproduction --dataset-version {m["dataset_version"]} '
            f'> {ROOT}/runs/sparse-reproduction-launch.log 2>&1 < /dev/null &')
        def existing_sparse():
            payload=remote(a.alias,f"/root/miniconda3/bin/python -c \"import pathlib,json; print(json.dumps([json.loads(p.read_text()) for p in pathlib.Path('{ROOT}/runs').glob('sparse-*/manifest.json')]))\"")
            candidates=[x for x in json.loads(payload) if x['phase']=='reproduction' and x['git_sha']==a.sha]
            if len(candidates)>1:raise RuntimeError('ambiguous sparse reproduction runs')
            return candidates[0]['run_id'] if candidates else None
        sparse=state.get('sparse_run') or existing_sparse()
        if sparse is None:remote(a.alias,command)
        for _ in range(30):
            sparse=sparse or existing_sparse()
            if sparse:break
            time.sleep(3)
        if sparse is None:raise RuntimeError('sparse run failed to start')
        state['sparse_run']=sparse
        m=wait(a.alias,sparse,'training',state,path)
        if m['evaluation_settings']['status']=='not_run':launch_plan(a.alias,a.sha,sparse)
        m=wait(a.alias,sparse,'evaluation',state,path)
        retain_checkpoint(a.alias,sparse,m)
        import sys
        sys.path.insert(0,str(REPO))
        from study.summarize_reproductions import summarize
        report=summarize(STORE,[a.gaussian_run,sparse],remote(a.alias,'df -hT / /root/autodl-tmp'))
        state.update(status='complete',stage='complete',report=str(report),updated_at=time.time())
    except BaseException as e:
        state.update(status='watcher_failed',error_type=type(e).__name__,error=str(e),updated_at=time.time())
        raise
    finally:record(path,state)

if __name__=='__main__':main()
