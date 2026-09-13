"""Versioned worker runner: bounded smokes and exact selected upstream training cells."""
import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from study.manifests import provenance, create_manifest, write_manifest, utcnow


def training_overrides(method, phase, seed, root, run_id):
    if method not in ('gaussian','sparse','pixel') or phase not in ('smoke','reproduction','pilot'):
        raise ValueError('invalid method/phase')
    if method == 'pixel' and phase == 'reproduction':
        raise ValueError('upstream has no temporal pixel reproduction')
    smoke = phase == 'smoke'
    common = ['--config-name', 'train_rdmreg.yaml', 'env=pusht', 'frameskip=5', 'num_hist=3',
              'encoder=vit_scratch', 'predictor=ar_adaln', 'encoder.proj_dim=384', 'action_emb_dim=384',
              'link='+('reprelu' if method=='sparse' else 'identity'),
              'target_p='+('1' if method=='sparse' else '2'), 'mu=0', 'agg=b',
              'regularizer=rdmreg', 'reg_weight=0.5', 'mup=true', 'training.mup_lr=1e-4',
              f'training.seed={seed}', f'training.epochs={1 if smoke else 2}',
              f'training.batch_size={2 if smoke else 64}', f'env.num_workers={0 if smoke else 20}',
              f'ckpt_base_path={root}/checkpoints',
              f'hydra.run.dir={root}/checkpoints/outputs/{run_id}']
    if smoke:
        common += ['env.dataset.n_rollout=2', 'training.num_reconstruct_samples=2']
    if method == 'pixel':
        common += ['model._target_=study.pixel.PixelWorldModel', 'decoder=study_pixel',
                   'has_decoder=true', 'model.train_decoder=true', 'reg_weight=0']
    return common


def worker_root_checked(value):
    root = Path(value).resolve()
    if not root.is_relative_to(Path('/root/autodl-tmp')):
        raise ValueError('runs must live under worker /root/autodl-tmp')
    mount = subprocess.check_output(['findmnt','-n','-o','TARGET','-T','/root/autodl-tmp'],text=True).strip()
    if mount == '/' or not mount:
        raise RuntimeError('worker data volume is not mounted separately')
    return root


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--method', choices=['gaussian','sparse','pixel'], required=True)
    p.add_argument('--phase', choices=['smoke','reproduction','pilot'], required=True)
    p.add_argument('--seed', type=int, default=0)
    p.add_argument('--worker-root', default='/root/autodl-tmp/robotics/jepa-worldmodel-study')
    p.add_argument('--dataset-version', required=True)
    a=p.parse_args()
    repo=Path(__file__).resolve().parents[1]
    info=provenance(repo)
    root=worker_root_checked(a.worker_root)
    import torch
    if not torch.cuda.is_available(): raise RuntimeError('CUDA worker required')
    if a.method == 'pixel' and a.phase == 'reproduction':
        raise ValueError('pixel has no official upstream reproduction')
    dataset=root/'datasets'
    for split in ('train','val'):
        for filename in ('states.pth','rel_actions.pth','velocities.pth','seq_lengths.pkl','obses'):
            if not (dataset/'pusht_noise'/split/filename).exists():
                raise FileNotFoundError(f'missing dataset component: {split}/{filename}')
    plan={'goal_horizon':5,'rollout_horizon':5,'execute_prefix':5,'max_replans':10,
          'cem_samples':300,'cem_elites':30,'cem_iterations':30,'frameskip':5,
          'simulator_early_stop':True,'protocol':'official_upstream'}
    folder, manifest=create_manifest(root/'runs',provenance_info=info,method=a.method,seed=a.seed,
        dataset_path=dataset/'pusht_noise',dataset_version=a.dataset_version,resolved_config=None,
        planning_settings=plan,evaluation_settings={'seed':99,'n_evals':50,'status':'not_run'})
    run_id=manifest['run_id']
    overrides=training_overrides(a.method,a.phase,a.seed,root,run_id)
    manifest.update(phase=a.phase, command_overrides=overrides, gpu_model=torch.cuda.get_device_name(0),
                    environment={'python':sys.version.split()[0], 'torch':torch.__version__,
                                 'cuda_runtime':torch.version.cuda, 'prefix':sys.prefix,
                                 'specification':'conf/study/worker-5090-requirements.txt',
                                 'constraints':'conf/study/worker-5090-constraints.txt'})
    env=os.environ.copy()
    env.update(DATASET_DIR=str(dataset),WANDB_MODE='offline',WANDB_DIR=str(folder),
               WANDB_CACHE_DIR=str(root/'caches/wandb'),HF_HOME=str(root/'caches/huggingface'),
               TORCH_HOME=str(root/'caches/torch'),TMPDIR=str(root/'caches/tmp'),
               PYTHONDONTWRITEBYTECODE='1',SDL_VIDEODRIVER='dummy',
               TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD='1',
               WORLD_SIZE='1',RANK='0',LOCAL_RANK='0',MASTER_ADDR='127.0.0.1')
    (root/'caches/tmp').mkdir(parents=True,exist_ok=True)
    with socket.socket() as sock:
        sock.bind(('',0)); env['MASTER_PORT']=str(sock.getsockname()[1])
    manifest['status']='resolving_config'; write_manifest(folder,manifest)
    monitor=None
    try:
        # Hydra config resolution is recorded before launching any training.
        with (folder/'resolved-config.yaml').open('w') as out:
            subprocess.run([sys.executable,'train.py',*overrides,'--cfg','job','--resolve'],
                           cwd=repo,env=env,stdout=out,stderr=subprocess.STDOUT,check=True)
        manifest['resolved_config']='resolved-config.yaml'
        manifest['training_start']=utcnow(); manifest['status']='running'
        write_manifest(folder,manifest)
        start=time.perf_counter()
        with (folder/'gpu-utilization.csv').open('w') as gpu:
            try:
                monitor=subprocess.Popen(['nvidia-smi','--query-gpu=timestamp,name,utilization.gpu,memory.used',
                                          '--format=csv','-l','2'],stdout=gpu,stderr=subprocess.DEVNULL)
            except FileNotFoundError: pass
            with (folder/'train.log').open('w') as out:
                result=subprocess.run([sys.executable,'-m','study.instrument','--telemetry',str(folder/'telemetry.json'),
                    '--smoke-batches',str(2 if a.phase=='smoke' else 0),'--',*overrides],cwd=repo,env=env,
                    stdout=out,stderr=subprocess.STDOUT)
        manifest['training_wall_seconds']=time.perf_counter()-start
        manifest['training_end']=utcnow(); manifest['exit_code']=result.returncode
        manifest['status']='training_complete' if result.returncode==0 else 'failed'
        if (folder/'telemetry.json').exists():
            manifest.update(json.loads((folder/'telemetry.json').read_text()))
        checkpoint=root/'checkpoints/outputs'/run_id/'checkpoints/model_latest.pth'
        if checkpoint.exists():
            manifest['checkpoint_path']=str(checkpoint)
            manifest['checkpoint_bytes']=checkpoint.stat().st_size
        if result.returncode==0 and not checkpoint.exists():
            manifest['status']='failed_missing_checkpoint'
    except BaseException as error:
        manifest['status']='failed'; manifest['error_type']=type(error).__name__
        manifest['training_end']=utcnow()
        raise
    finally:
        if monitor is not None:
            monitor.terminate(); monitor.wait()
        write_manifest(folder,manifest)
    print(folder/'manifest.json')
    if manifest['status'] != 'training_complete': raise SystemExit(1)

if __name__=='__main__': main()
