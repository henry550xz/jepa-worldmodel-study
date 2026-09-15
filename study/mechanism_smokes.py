"""Sequential, bounded four-arm smoke queue; deliberately no full-training mode."""
import os,json,time,subprocess,sys,socket,uuid,argparse,hashlib,fcntl
from pathlib import Path
from study.run import worker_root_checked,training_overrides
from study.manifests import provenance
from study.mechanism import ARMS

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();root=worker_root_checked('/root/autodl-tmp/robotics/jepa-worldmodel-study');repo=Path(__file__).resolve().parents[1];info=provenance(repo);spec=json.loads((repo/'conf/study/mechanism.json').read_text())
 assert spec['arms']==list(ARMS) and not spec['full_training_authorized']
 with (root/'runs/mechanism-smokes.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);out=root/'runs'/a.output;out.mkdir(exist_ok=False);queue={'status':'running','sha':info['git_sha'],'runs':{},'full_runs_authorized':False};(out/'state.json').write_text(json.dumps(queue,indent=2))
  env=dict(os.environ,DATASET_DIR=str(root/'datasets'),WANDB_MODE='offline',WANDB_DIR=str(out),WANDB_CACHE_DIR=str(root/'caches/wandb'),TORCH_HOME=str(root/'caches/torch'),TMPDIR=str(root/'caches/tmp'),MPLCONFIGDIR=str(root/'caches/matplotlib'),XDG_CACHE_HOME=str(root/'caches/xdg'),PYTHONDONTWRITEBYTECODE='1',SDL_VIDEODRIVER='dummy',TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD='1',WORLD_SIZE='1',RANK='0',LOCAL_RANK='0',MASTER_ADDR='127.0.0.1')
  try:
   for arm in ARMS:
    rid=f'mechanism-{arm}-s0-'+uuid.uuid4().hex[:12];folder=root/'runs'/rid;folder.mkdir();overrides=training_overrides('pixel','readiness',spec['seed'],root,rid)+[f"num_hist={spec['history']}",f"num_pred={spec['training_horizon']}",f"frameskip={spec['frameskip']}",f"training.batch_size={spec['batch_size']}",f"training.mup_lr={spec['learning_rate']}",'model._target_=study.mechanism.MechanismWorldModel',f'+model.mechanism={arm}',f"+model.training_horizon={spec['training_horizon']}",f"+model.consistency_weight={spec['latent_consistency_weight']}",f"reg_weight={spec['gaussian_regularizer_weight']}",f"detach_target={str(spec['detach_target']).lower()}"]
    m={'run_id':rid,'method':'gaussian' if arm=='gaussian' else 'pixel','mechanism':arm,'phase':'readiness','purpose':'bounded mechanism smoke, not research results',**info,'status':'running','overrides':overrides,'training_start':time.time(),'partitions_sha256':hashlib.sha256((repo/'manifests/PUSHT_PARTITIONS.json').read_bytes()).hexdigest()};(folder/'manifest.json').write_text(json.dumps(m,indent=2));queue['runs'][arm]=rid;queue['active_arm']=arm;(out/'state.json').write_text(json.dumps(queue,indent=2))
    with socket.socket() as sock:sock.bind(('',0));env['MASTER_PORT']=str(sock.getsockname()[1])
    with (folder/'resolved-config.yaml').open('w') as conf,(folder/'resolve.log').open('w') as log:subprocess.run([sys.executable,'train.py',*overrides,'--cfg','job','--resolve'],cwd=repo,env=env,stdout=conf,stderr=log,check=True)
    with (folder/'train.log').open('w') as log:subprocess.run([sys.executable,'-u','-m','study.mechanism_instrument','--telemetry',str(folder/'telemetry.json'),'--',*overrides],cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    cp=root/'checkpoints/outputs'/rid/'checkpoints/model_latest.pth';assert cp.exists();actual=cp.parents[1]/'hydra.yaml';(folder/'resolved-config.yaml').write_bytes(actual.read_bytes());m.update(status='training_complete',checkpoint_path=str(cp),checkpoint_bytes=cp.stat().st_size,training_end=time.time());(folder/'manifest.json').write_text(json.dumps(m,indent=2));print('TRAIN_SMOKE_PASSED',arm,rid,flush=True)
   queue['status']='training_smokes_passed'
  except BaseException as e:queue.update(status='failed',error=str(e));raise
  finally:(out/'state.json').write_text(json.dumps(queue,indent=2)+'\n')
if __name__=='__main__':main()
