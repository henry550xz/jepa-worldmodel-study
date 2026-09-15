"""Frozen-checkpoint inference diagnostics; never fits models or probes."""
import os,json,time,argparse,hashlib
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 root=Path('/root/autodl-tmp/robotics/jepa-worldmodel-study')
 os.environ.update(DATASET_DIR=str(root/'datasets'),TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD='1',SDL_VIDEODRIVER='dummy',WANDB_MODE='offline',TMPDIR=str(root/'caches/tmp'),MPLCONFIGDIR=str(root/'caches/matplotlib'),XDG_CACHE_HOME=str(root/'caches/xdg'),TORCH_HOME=str(root/'caches/torch'))
 import torch,numpy as np
 from PIL import Image,ImageDraw
 from study.adapters import CheckpointAdapter
 from study.manifests import provenance
 from datasets.pusht_dset import PushTDataset
 from datasets.img_transforms import default_transform
 torch.set_num_threads(4);out=root/'artifacts'/a.output;out.mkdir(exist_ok=False)
 rid='pixel-s0-20260914T230335-3649012fd387';folder=root/'runs'/rid;m=json.loads((folder/'manifest.json').read_text());ad=CheckpointAdapter.load(m['checkpoint_path'],folder/'resolved-config.yaml');model=ad.model
 base=json.loads(next(folder.glob('common-pilot-*/metrics.json')).read_text());ids=base['probe_episode_selection']['probe_test'];data=PushTDataset(data_path=str(root/'datasets/pusht_noise/train'),transform=default_transform());horizons=[1,2,4,8,16,32];rows=[];start=time.time()
 def cpu(x):return ((x.detach().cpu().numpy()+1)/2).clip(0,1)
 def edge(x):return float(np.mean(np.diff(x,axis=-1)**2)+np.mean(np.diff(x,axis=-2)**2))
 with torch.inference_mode():
  for num,idx in enumerate(ids):
   H=min(32,(data.get_seq_length(idx)-11)//5);stop=11+5*H;obs,actions,states,_=data.get_frames(idx,list(range(stop)));hist={k:v[None,[0,5,10]].cuda() for k,v in obs.items()};act=actions[:stop-1].reshape(1,H+2,10).cuda();z,_=model.rollout(hist,act);frames=[]
   for h in horizons:
    if h>H:continue
    t=10+5*h;true={k:v[None,t:t+1].cuda() for k,v in obs.items()};zt=model.encode_obs_linked(true)['visual'];pred=z['visual'][:,2+h:3+h];de=model.decode_obs({'visual':zt})[0]['visual'];dp=model.decode_obs({'visual':pred})[0]['visual']
    th={k:v[None,[t-15,t-10,t-5]].cuda() for k,v in obs.items()};ta=actions[t-15:t].reshape(1,3,10).cuda();tz,_=model.rollout(th,ta);dt=model.decode_obs({'visual':tz['visual'][:,-1:]})[0]['visual']
    imgs=[cpu(true['visual'])[0,0],cpu(de)[0,0],cpu(dp)[0,0],cpu(dt)[0,0]];gt=imgs[0]
    rows.append({'episode':idx,'horizon':h,'state':states[t,:5].tolist(),'metrics':{name:{'image_mse':float(np.mean((im-gt)**2)),'edge_energy':edge(im),'edge_ratio':edge(im)/max(edge(gt),1e-12)} for name,im in zip(['truth','decode_true','rollout','teacher_forced'],imgs)}})
    frames.append((h,imgs))
   # Save every evaluated frame, losslessly quantized for image-only segmentation diagnostics.
   for h,imgs in frames:
    for name,im in zip(['truth','decode_true','rollout','teacher_forced'],imgs):Image.fromarray((im.transpose(1,2,0)*255).round().astype('uint8')).save(out/f'ep{idx}-h{h}-{name}.png')
   if H==32 or num<2:
    canvas=Image.new('RGB',(6*224,4*248),'white');draw=ImageDraw.Draw(canvas)
    for h,imgs in frames:
     c=horizons.index(h)
     for row,(name,im) in enumerate(zip(['ground truth','D(E(true))','D(rollout)','D(teacher forced)'],imgs)):
      canvas.paste(Image.fromarray((im.transpose(1,2,0)*255).round().astype('uint8')),(c*224,row*248+24));draw.text((c*224+4,row*248+4),f'{name} h={h}',fill='black')
    canvas.save(out/f'panel-ep{idx}.png')
   print(f'episode {num+1}/{len(ids)} id={idx}',flush=True)
 result={'diagnostic_sha':provenance(Path(__file__).resolve().parents[1])['git_sha'],'training_sha':m['git_sha'],'run_id':rid,'seconds':time.time()-start,'rows':rows,'peak_vram_bytes':torch.cuda.max_memory_allocated(),'no_training':True}
 (out/'metrics.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print('COMPLETE',out,flush=True)
if __name__=='__main__':main()
