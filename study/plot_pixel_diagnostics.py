"""Export physical-error curves from retained pilot metrics."""
import json,argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
 p=argparse.ArgumentParser();p.add_argument('storage');a=p.parse_args();r=Path(a.storage);rows=json.loads((r/'runs/pilot-summary.json').read_text());out=r/'artifacts/pixel-diagnostics-20260915'
 fig,axes=plt.subplots(1,3,figsize=(14,4.5))
 colors={'pixel':'#c34c3d','gaussian':'#326ca6','sparse':'#27845b'}
 for ax,key,label in zip(axes,['pusher_position_rmse','block_position_rmse','angle_mae_rad'],['Pusher position RMSE (environment units)','Block position RMSE (environment units)','Block angle MAE (radians)']):
  for row in rows:
   h=[1,2,4,8,16,32]
   for typ,style in [('prediction','-'),('representation','--')]:ax.plot(h,[row['horizons'][str(i)][typ][key] for i in h],style,marker='o',color=colors[row['method']],label=row['method']+' '+typ)
  ax.set_xscale('log',base=2);ax.set_xticks(h,labels=h);ax.set_xlabel('Rollout horizon (5 simulator steps each)');ax.set_ylabel(label);ax.grid(alpha=.2)
 axes[0].legend(fontsize=7);fig.suptitle('Held-out physical errors: frozen linear probe; solid predicted, dashed true-future encoding\nN = 124,124,124,124,106,4; changing horizon cohorts, one training seed',fontsize=11);fig.tight_layout();fig.savefig(out/'physical-error-horizons.png',dpi=160);fig.savefig(out/'physical-error-horizons.pdf');plt.close(fig)
if __name__=='__main__':main()
