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
  def rollout_latents(self,history,actions):
   obs={k:v.cuda() for k,v in history['observations'].items()};acts=torch.as_tensor(np.ascontiguousarray(actions) if isinstance(actions,np.ndarray) else actions,device='cuda',dtype=torch.float32);allacts=torch.cat([history['actions'].cuda(),acts],1);emb=self.model.encode_obs_linked(obs)['visual'];future=[]
   for _ in range(acts.shape[1]):
    # Same prefix and batch shape regardless of requested future horizon.
    encoded=self.model.encode_act(allacts[:,:emb.shape[1]].contiguous());pred=self.model._predict_next_adaln(emb,encoded);future.append(pred);emb=torch.cat([emb,pred],1)
   return torch.cat(future,1)
  @torch.no_grad()
  def predict_states(self,history,actions):
   future=self.rollout_latents(history,actions);results=[]
   for t in range(future.shape[1]):
    z=future[:,t:t+1]
    if self.model.mechanism=='gaussian':features=z.flatten(2)
    else:
     image=self.model.decode_obs({'visual':z})[0]['visual'];features=self.features({'visual':image})
    results.append(physical_states(self.probe(features)).cpu().numpy())
   return np.concatenate(results,1)
 evaluation.CheckpointAdapter=CompatibleAdapter;evaluation.run(root,a.run_id,'readiness')
 # Extend completed smoke report with closure against true future encodings.
 folder=root/'runs'/a.run_id;report_path=folder/('common-readiness-'+evaluation.provenance(Path(__file__).resolve().parents[1])['git_sha'][:12])/'metrics.json';report=json.loads(report_path.read_text());m=json.loads((folder/'manifest.json').read_text());ad=CompatibleAdapter.load(m['checkpoint_path'],folder/'resolved-config.yaml')
 from datasets.pusht_dset import PushTDataset
 from datasets.img_transforms import default_transform
 data=PushTDataset(data_path=str(root/'datasets/pusht_noise/train'),transform=default_transform());results=[]
 with torch.no_grad():
  for idx in report['probe_episode_selection']['probe_test']:
   H=min(32,(data.get_seq_length(idx)-11)//5);stop=11+H*5;obs,act,_,_=data.get_frames(idx,list(range(stop)));hist={k:v[None,[0,5,10]].cuda() for k,v in obs.items()};pred=ad.rollout_latents({'observations':hist,'actions':act[:10].reshape(1,2,10)},act[10:stop-1].reshape(1,H,10));truth=torch.cat([ad.model.encode_obs_linked({'visual':obs['visual'][None,t:t+1].cuda()})['visual'] for t in range(15,stop,5)],1)
   reference=truth.flatten(0,1).var(dim=0,unbiased=False).mean();cycles={}
   if ad.model.mechanism!='gaussian':
    for h in [1,2,4,8,16,32]:
     if h<=H:
      zp=pred[:,h-1:h];image=ad.model.decode_obs({'visual':zp})[0]['visual'];ze=ad.model.encode_obs_linked({'visual':image})['visual'];cycles[str(h)]=latent_closure(zp,ze,reference_variance=reference)
   results.append({'episode':idx,'horizons':{str(h):latent_closure(pred[:,h-1:h],truth[:,h-1:h],reference_variance=reference) for h in [1,2,4,8,16,32] if h<=H},'decode_reencode_cycle':cycles if cycles else {'status':'not_applicable_untrained_gaussian_decoder'}})
 report['latent_closure']=results;report['readout']='raw encoded-space Gaussian; frozen E(D(predicted)) pixel; raw latent closure reported separately';report_path.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
