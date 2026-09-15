"""Shared readiness evaluator with declared, compatible observation readout."""
import os,argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('run_id');a=p.parse_args()
 from study.run import worker_root_checked
 root=worker_root_checked('/root/autodl-tmp/robotics/jepa-worldmodel-study');os.environ.update(DATASET_DIR=str(root/'datasets'),TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD='1',SDL_VIDEODRIVER='dummy',WANDB_MODE='offline',TMPDIR=str(root/'caches/tmp'),MPLCONFIGDIR=str(root/'caches/matplotlib'),XDG_CACHE_HOME=str(root/'caches/xdg'),TORCH_HOME=str(root/'caches/torch'))
 import torch,numpy as np
 from study.adapters import CheckpointAdapter
 from study.probes import physical_states
 from study.mechanism import latent_closure
 from study import readiness_eval as evaluation
 class CompatibleAdapter(CheckpointAdapter):
  @torch.no_grad()
  def predict_states(self,history,actions):
   if self.model.mechanism=='gaussian':return super().predict_states(history,actions)
   obs={k:v.cuda() for k,v in history['observations'].items()};acts=torch.as_tensor(np.ascontiguousarray(actions) if isinstance(actions,np.ndarray) else actions,device='cuda',dtype=torch.float32);z,_=self.model.rollout(obs,torch.cat([history['actions'].cuda(),acts],1));future=z['visual'][:,obs['visual'].shape[1]:];B,T=future.shape[:2];flat=future.reshape(B*T,1,*future.shape[2:]);results=[]
   for i in range(0,len(flat),4):
    decoded=self.model.decode_obs({'visual':flat[i:i+4]})[0]['visual'];encoded=self.features({'visual':decoded});results.append(physical_states(self.probe(encoded)).cpu().numpy())
   return np.concatenate(results,0).reshape(B,T,-1)
 evaluation.CheckpointAdapter=CompatibleAdapter;evaluation.run(root,a.run_id,'readiness')
 # Extend completed smoke report with closure against true future encodings.
 folder=root/'runs'/a.run_id;report_path=next(folder.glob('common-readiness-*/metrics.json'));report=json.loads(report_path.read_text());m=json.loads((folder/'manifest.json').read_text());ad=CompatibleAdapter.load(m['checkpoint_path'],folder/'resolved-config.yaml')
 from datasets.pusht_dset import PushTDataset
 from datasets.img_transforms import default_transform
 data=PushTDataset(data_path=str(root/'datasets/pusht_noise/train'),transform=default_transform());results=[]
 with torch.no_grad():
  for idx in report['probe_episode_selection']['probe_test']:
   H=min(32,(data.get_seq_length(idx)-11)//5);stop=11+H*5;obs,act,_,_=data.get_frames(idx,list(range(stop)));hist={k:v[None,[0,5,10]].cuda() for k,v in obs.items()};z,_=ad.model.rollout(hist,act[:stop-1].reshape(1,H+2,10).cuda());pred=z['visual'][:,3:];truth=torch.cat([ad.model.encode_obs_linked({'visual':obs['visual'][None,t:t+1].cuda()})['visual'] for t in range(15,stop,5)],1)
   results.append({'episode':idx,'horizons':{str(h):latent_closure(pred[:,h-1:h],truth[:,h-1:h],reference_variance=truth.flatten(0,1).var(dim=0,unbiased=False).mean()) for h in [1,2,4,8,16,32] if h<=H}})
 report['latent_closure']=results;report['readout']='raw encoded-space Gaussian; frozen E(D(predicted)) pixel; raw latent closure reported separately';report_path.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
