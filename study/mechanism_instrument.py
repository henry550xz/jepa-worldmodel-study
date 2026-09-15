"""Bounded real-architecture/data smoke path; no full-run entry point."""
import argparse,json,sys,time,itertools,hashlib
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--telemetry',required=True);p.add_argument('overrides',nargs=argparse.REMAINDER);a=p.parse_args()
    import torch,train
    from study.mechanism import latent_closure
    stats={'status':'running','steps':[]};initial={};work={}
    def run_epoch(self,training):
        self.model.train(training);limit=8 if training else 2
        loader=iter(self.dataloaders['train' if training else 'valid']);last=time.perf_counter()
        for i in range(limit):
            obs,act,state=next(loader);wait=time.perf_counter()-last
            if training and i==0:
                for n in ['encoder','predictor','action_encoder','decoder']:
                    module=getattr(self,n);h=hashlib.sha256()
                    for v in module.state_dict().values():h.update(v.detach().cpu().numpy().tobytes())
                    initial[n]=h.hexdigest()
                stats['first_batch_sha256']=hashlib.sha256(obs['visual'].detach().cpu().numpy().tobytes()+act.detach().cpu().numpy().tobytes()).hexdigest()
            opts=[getattr(self,n,None) for n in ['encoder_optimizer','predictor_optimizer','action_encoder_optimizer','decoder_optimizer']]
            for opt in opts:
                if opt:opt.zero_grad(set_to_none=True)
            work.clear();torch.cuda.synchronize();start=time.perf_counter()
            with torch.set_grad_enabled(training):
                pred,_,_,loss,parts=self.model(obs,act)
                if not torch.isfinite(loss):raise RuntimeError('nonfinite mechanism loss')
                if training:
                    self.accelerator.backward(loss)
                    if i in (0,3):
                        grad={n:sum(float(p.grad.abs().sum()) for p in getattr(self,n).parameters() if p.grad is not None) for n in ['encoder','predictor','action_encoder','decoder']}
                        required=['encoder','predictor']+(['decoder'] if self.model.mechanism!='gaussian' else [])+(['action_encoder'] if i>=3 else [])
                        assert all(grad[n]>0 for n in required),(self.model.mechanism,grad)
                        stats.setdefault('gradients',{})[str(i)]=grad
                    for opt in opts:
                        if opt:opt.step()
            torch.cuda.synchronize();elapsed=time.perf_counter()-start
            stats['steps'].append({'training':training,'step':i,'seconds':elapsed,'loader_seconds':wait,'batch':len(act),'module_work':dict(work),'losses':{k:float(v.detach()) for k,v in parts.items()}})
            self.logs_update({('train_' if training else 'val_')+'loss':[float(loss.detach())]})
            if not training:
                with torch.no_grad():
                    history={k:v[:,:3] for k,v in obs.items()};z,_=self.model.rollout(history,act[:,:5]);truth=self.model.encode_obs_linked({k:v[:,3:6] for k,v in obs.items()})['visual'];stats.setdefault('latent_closure',[]).append(latent_closure(z['visual'][:,3:6],truth))
            last=time.perf_counter();print(self.model.mechanism,'train' if training else 'validation',i+1,float(loss.detach()),flush=True)
    train.Trainer.train=lambda self:run_epoch(self,True);train.Trainer.val=lambda self:run_epoch(self,False)
    original=train.Trainer.init_models
    def init(self):
        original(self)
        def counter(name):
            def hook(module,args,out):
                x=args[0];n=x.shape[0] if name=='encoder' else x.shape[0]*x.shape[1];work[name]=work.get(name,0)+int(n)
            return hook
        for name in ['encoder','predictor','action_encoder','decoder']:getattr(self,name).register_forward_hook(counter(name))
        stats['parameters']={n:sum(p.numel() for p in getattr(self,n).parameters()) for n in ['encoder','predictor','action_encoder','decoder']}
    train.Trainer.init_models=init
    torch.cuda.reset_peak_memory_stats();start=time.time();sys.argv=['train.py','--config-path',str(Path(train.__file__).resolve().parent/'conf')]+(a.overrides[1:] if a.overrides[:1]==['--'] else a.overrides)
    try:train.main();stats['status']='passed'
    except BaseException as e:stats.update(error_type=type(e).__name__,error=str(e));raise
    finally:
        stats.update(initial_module_sha256=initial,wall_seconds=time.time()-start,peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved());Path(a.telemetry).write_text(json.dumps(stats,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
