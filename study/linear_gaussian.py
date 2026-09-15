"""Provisional rank-one state+nuisance model, NOT an unspecified external theory.

Stationary unit-variance s,n; s'=alpha*s+sqrt(1-alpha^2)*eps_s,
n'=rho*n+sqrt(1-rho^2)*eps_n; x=(s,beta*n).
For rank-one linear future-observation prediction, explained eigenvalues are
alpha^2 and beta^2*rho^2. State selected iff alpha^2>beta^2*rho^2.
For a fixed whitened future target, eigenvalues alpha^2,rho^2. This is a
whitened-target reference, not a claim about jointly learned JEPA objectives.
"""
import argparse,json
from pathlib import Path
import numpy as np

def sample(n,alpha,beta,rho,rng):
 if not (-1<alpha<1 and -1<rho<1 and beta>0):raise ValueError('stationary correlations and positive nuisance scale required')
 z=rng.normal(size=(n,2));future=z*np.array([alpha,rho])+rng.normal(size=(n,2))*np.sqrt(1-np.array([alpha,rho])**2)
 return z*np.array([1,beta]),future*np.array([1,beta]),future[:,0]

def fit_rank_one(x,y):
 xm=x.mean(0);ym=y.mean(0);x=x-xm;y=y-ym;cov=x.T@x/len(x);v,u=np.linalg.eigh(cov);whiten=(u*(1/np.sqrt(v)))@u.T;cross=y.T@x@whiten/len(x);_,_,vt=np.linalg.svd(cross,full_matrices=False);encoder=whiten@vt[0];z=x@encoder;decoder=z@y/(z@z);return xm,ym,encoder,decoder

def experiment(alpha,beta,rho,seed=0,n_train=10000,n_test=20000):
 rng=np.random.default_rng(seed);x,y,st=sample(n_train,alpha,beta,rho,rng);xt,yt,stt=sample(n_test,alpha,beta,rho,rng);out={}
 for kind in ['pixel','fixed_whitened_target']:
  scale=np.ones(2) if kind=='pixel' else y.std(0);fit=fit_rank_one(x,y/scale);xm,ym,w,decoder=fit;z=(x-xm)@w;zt=(xt-xm)@w;prediction=(zt[:,None]*decoder+ym)*scale
  # Probe fitted on training data only; evaluate future relevant-state readout.
  state_weight=np.linalg.lstsq(np.stack([z,np.ones(len(z))],1),st,rcond=None)[0];sp=np.stack([zt,np.ones(len(zt))],1)@state_weight
  state_fraction=float(w[0]**2/(w[0]**2+(beta*w[1])**2));margin=alpha**2-(beta*rho)**2 if kind=='pixel' else alpha**2-rho**2
  out[kind]={'analytic_state_selected':bool(margin>0),'analytic_margin':margin,'empirical_state_loading_fraction':state_fraction,'state_prediction_mse':float(np.mean((sp-stt)**2)),'image_prediction_mse':float(np.mean((prediction-yt)**2))}
 return {'alpha':alpha,'beta':beta,'rho':rho,'seed':seed,'n_train':n_train,'n_test':n_test,'results':out}

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--alpha',type=float,default=.8);a=p.parse_args();rows=[experiment(a.alpha,b,r,seed=0) for b in [.25,.5,1,2,4] for r in [0,.2,.5,.8,.95]];out=Path(a.output);out.mkdir(exist_ok=False);(out/'results.json').write_text(json.dumps({'status':'provisional_theory_definition_unconfirmed','definition':__doc__,'rows':rows},indent=2)+'\n');print('Completed25 CPU-only cells; proposed user theory still requires definitions')
if __name__=='__main__':main()
