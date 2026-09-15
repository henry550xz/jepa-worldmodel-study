"""Guarded sequential authorized four-arm training and common evaluation queue."""
import os,json,time,subprocess,sys,socket,uuid,argparse,hashlib,fcntl
from pathlib import Path
from study.run import worker_root_checked,training_overrides
from study.manifests import provenance
from study.mechanism import ARMS

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--authorized-full',action='store_true',required=True);a=p.parse_args();root=worker_root_checked('/root/autodl-tmp/robotics/jepa-worldmodel-study');repo=Path(__file__).resolve().parents[1];info=provenance(repo);spec=json.loads((repo/'conf/study/mechanism.json').read_text())
 assert spec['arms']==list(ARMS) and spec['full_training_authorized']
 with (root/'runs/mechanism-full.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);out=root/'runs'/a.output;out.mkdir(exist_ok=False);queue={'status':'running','sha':info['git_sha'],'runs':{},'full_runs_authorized':True};(out/'state.json').write_text(json.dumps(queue,indent=2))
  env=dict(os.environ,DATASET_DIR=str(root/'datasets'),WANDB_MODE='offline',WANDB_DIR=str(out),WANDB_CACHE_DIR=str(root/'caches/wandb'),TORCH_HOME=str(root/'caches/torch'),TMPDIR=str(root/'caches/tmp'),MPLCONFIGDIR=str(root/'caches/matplotlib'),XDG_CACHE_HOME=str(root/'caches/xdg'),PYTHONDONTWRITEBYTECODE='1',SDL_VIDEODRIVER='dummy',TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD='1',WORLD_SIZE='1',RANK='0',LOCAL_RANK='0',MASTER_ADDR='127.0.0.1')
  gpu_log=(out/'gpu-utilization.csv').open('w');gpu=subprocess.Popen(['nvidia-smi','--query-gpu=timestamp,utilization.gpu,memory.used','--format=csv','-l','10'],stdout=gpu_log)
  try:
   for arm in ARMS:
    import shutil
    if shutil.disk_usage(root).free < 4*1024**3:raise RuntimeError('Less than4GiB data disk headroom; queue stopped')
    rid=a.output+'-'+arm;folder=root/'runs'/rid;folder.mkdir();overrides=training_overrides('pixel','pilot',spec['seed'],root,rid)+[f"num_hist={spec['history']}",f"num_pred={spec['training_horizon']}",f"frameskip={spec['frameskip']}",f"training.batch_size={spec['batch_size']}",f"training.mup_lr={spec['learning_rate']}",'model._target_=study.mechanism.MechanismWorldModel',f'+model.mechanism={arm}',f"+model.training_horizon={spec['training_horizon']}",f"+model.consistency_weight={spec['latent_consistency_weight']}",f"reg_weight={spec['gaussian_regularizer_weight']}",f"detach_target={str(spec['detach_target']).lower()}"]
    import torch
    m={'python_version':sys.version,'torch_version':torch.__version__,'cuda_runtime':torch.version.cuda,'gpu_model':torch.cuda.get_device_name(0),'mechanism_config':spec,'dataset_path':str(root/'datasets/pusht_noise'),'dataset_version':'442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08','run_id':rid,'method':'gaussian' if arm=='gaussian' else 'pixel','mechanism':arm,'phase':'pilot','purpose':'authorized four-arm seed0 matched-window mechanism experiment',**info,'status':'running','overrides':overrides,'training_start':time.time(),'partitions_sha256':hashlib.sha256((repo/'manifests/PUSHT_PARTITIONS.json').read_bytes()).hexdigest()};(folder/'manifest.json').write_text(json.dumps(m,indent=2));queue['runs'][arm]=rid;queue['active_arm']=arm;queue['stage']='training';(out/'state.json').write_text(json.dumps(queue,indent=2))
    with socket.socket() as sock:sock.bind(('',0));env['MASTER_PORT']=str(sock.getsockname()[1])
    with (folder/'resolved-config.yaml').open('w') as conf,(folder/'resolve.log').open('w') as log:subprocess.run([sys.executable,'train.py',*overrides,'--cfg','job','--resolve'],cwd=repo,env=env,stdout=conf,stderr=log,check=True)
    with (folder/'train.log').open('w') as log:subprocess.run([sys.executable,'-u','-m','study.instrument','--telemetry',str(folder/'telemetry.json'),'--matched','--',*overrides],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    cp=root/'checkpoints/outputs'/rid/'checkpoints/model_latest.pth';assert cp.exists();actual=cp.parents[1]/'hydra.yaml';(folder/'resolved-config.yaml').write_bytes(actual.read_bytes());m.update(status='training_complete',checkpoint_path=str(cp),checkpoint_bytes=cp.stat().st_size,training_end=time.time());(folder/'manifest.json').write_text(json.dumps(m,indent=2));print('TRAINING_COMPLETE',arm,rid,flush=True)
    queue['stage']='evaluation';(out/'state.json').write_text(json.dumps(queue,indent=2))
    with (folder/'evaluation.log').open('w') as log:subprocess.run([sys.executable,'-u','-m','study.mechanism_evaluate',rid,'--profile','pilot'],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    metrics=folder/('common-pilot-'+info['git_sha'][:12])/'metrics.json';result=json.loads(metrics.read_text());assert result['status']=='passed' and result.get('latent_closure')
    queue.setdefault('completed',[]).append(rid);print('ARM_COMPLETE',arm,rid,flush=True)
   queue['status']='complete';queue['stage']='complete'
  except BaseException as e:queue.update(status='failed',error=str(e));raise
  finally:
   gpu.terminate();gpu.wait();gpu_log.close();(out/'state.json').write_text(json.dumps(queue,indent=2)+'\n')
if __name__=='__main__':main()
