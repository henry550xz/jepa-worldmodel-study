"""Postprocess saved diagnostic images; no fitting or model execution."""
import argparse,json,math
from pathlib import Path
import numpy as np
from PIL import Image

def block_mask(a):
 r,g,b=a.transpose(2,0,1)
 return (r>.25)&(r<.8)&(g-r>.02)&(g-r<.16)&(b-g>0)&(b-g<.14)&(b-r>.04)

def pose(mask):
 y,x=np.where(mask)
 if len(x)<25:return None
 pts=np.stack([x,y],1);center=pts.mean(0);vals,vecs=np.linalg.eigh(np.cov(pts.T));v=vecs[:,-1]
 return center,math.atan2(v[1],v[0]),float((vals[-1]-vals[0])/max(vals[-1],1e-8))

def main():
 p=argparse.ArgumentParser();p.add_argument('folder');a=p.parse_args();root=Path(a.folder);d=json.loads((root/'metrics.json').read_text());records=[]
 for row in d['rows']:
  idx,h=row['episode'],row['horizon'];imgs={name:np.array(Image.open(root/f'ep{idx}-h{h}-{name}.png')).astype(float)/255 for name in ['truth','decode_true','rollout','teacher_forced']};gt=imgs['truth'];mask=block_mask(gt);pgt=pose(mask);assert pgt is not None
  white=(gt.min(-1)>.95);dynamic=mask|((gt[:,:,2]-gt[:,:,1]>.15)&(gt[:,:,2]-gt[:,:,0]>.15));stats={}
  for name,im in imgs.items():
   m=block_mask(im);pm=pose(m);ratio=float(m.sum()/mask.sum());valid=pm is not None and .1<=ratio<=3 and pm[2]>.05
   delta=(pm[1]-pgt[1]) if valid else None
   stats[name]={'block_area_ratio':ratio,'pose_valid':valid,'centroid_error_px':float(np.linalg.norm(pm[0]-pgt[0])) if valid else None,'axis_error_rad':float(abs((delta+np.pi/2)%np.pi-np.pi/2)) if valid else None,'white_background_fraction':float(white.mean()),'dynamic_fraction':float(dynamic.mean()),'dynamic_mse':float(((im-gt)**2)[dynamic].mean()),'white_background_mse':float(((im-gt)**2)[white].mean()),'dynamic_sse_fraction':float(((im-gt)**2)[dynamic].sum()/max(((im-gt)**2).sum(),1e-20)),**row['metrics'][name]}
  records.append({'episode':idx,'horizon':h,'metrics':stats})
 aggregate={}
 for h in [1,2,4,8,16,32]:
  rs=[r for r in records if r['horizon']==h];aggregate[str(h)]={'n':len(rs),'methods':{}}
  for name in ['decode_true','rollout','teacher_forced']:
   vals=[r['metrics'][name] for r in rs];out={}
   for k in vals[0]:
    v=[x[k] for x in vals if x[k] is not None];out[k]=float(np.mean(v)) if v else None
   out['pose_valid_count']=sum(v['pose_valid'] for v in vals);aggregate[str(h)]['methods'][name]=out
 result={'aggregate':aggregate,'rows':records,'pose_definition':'RGB gray-blue block mask; centroid of mask; PCA undirected axis modulo pi. Valid if >=25 pixels, area 0.1..3 times GT and eigenvalue anisotropy >0.05. Conditional errors exclude invalid detections; not a calibrated full physical heading estimator.'}
 (root/'image-summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 print(json.dumps(aggregate,indent=2))
if __name__=='__main__':main()
