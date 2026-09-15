"""Four matched-window objectives; upstream modules and rollout preserved."""
import torch
from models.visual_world_model import VWorldModel
ARMS=('pixel','pixel_rollout','pixel_consistency','gaussian')

class MechanismWorldModel(VWorldModel):
    def __init__(self,*args,mechanism='pixel',training_horizon=3,consistency_weight=1.,**kwargs):
        super().__init__(*args,**kwargs)
        if mechanism not in ARMS or self.action_conditioning!='adaln':raise ValueError('unsupported mechanism')
        if training_horizon<1 or consistency_weight<0:raise ValueError('invalid objective')
        self.mechanism=mechanism;self.training_horizon=training_horizon;self.consistency_weight=consistency_weight
        if self.decoder is None:raise ValueError('all configurations instantiate the same decoder; Gaussian leaves it dormant')

    def _forward_adaln(self,obs,act):
        h,k=self.num_hist,self.training_horizon
        if obs['visual'].shape[1]!=h+k or act.shape[1]<h+k-1:raise ValueError('matched history plus future targets required')
        # Encoder sees true frames only for teacher forcing or explicit target losses.
        n=h if self.mechanism=='pixel_rollout' else h+k-1 if self.mechanism=='pixel' else h+k
        encoded=self.encode_obs_linked({key:v[:,:n] for key,v in obs.items()})['visual']
        action=self.encode_act(act[:,:h+k-1]);context=encoded[:,:h];predictions=[]
        for i in range(k):
            source=context[:,-h:] if self.mechanism=='pixel_rollout' else encoded[:,i:i+h]
            pred=self._link(self.predict(source,action[:,i:i+h])[:,-1:]);predictions.append(pred)
            if self.mechanism=='pixel_rollout':context=torch.cat([context,pred],1) # no detach, no future images
        predicted=torch.cat(predictions,1);parts={};loss=predicted.new_zeros(());images=None
        if self.mechanism!='gaussian':
            images=self.decode_obs({'visual':predicted})[0]['visual'];px=self.decoder_criterion(images,obs['visual'][:,h:h+k]);loss=loss+px;parts['pixel_loss']=px
        if self.mechanism in ('pixel_consistency','gaussian'):
            target=encoded[:,h:h+k];target=target.detach() if self.detach_target else target
            latent=self.emb_criterion(predicted,target);parts['latent_loss']=latent;loss=loss+latent*(self.consistency_weight if self.mechanism=='pixel_consistency' else 1.)
        if self.mechanism=='gaussian':
            reg=self.regularizer.reg_loss(encoded,link=self.link);parts['regularizer_loss']=reg;loss=loss+self.reg_weight*reg
        parts['loss']=loss
        return predicted,images,None,loss,parts


def latent_closure(predicted,target,reference_variance=None):
    """Diagnostic only. A near-zero variance denominator is flagged, not hidden."""
    diff=(predicted-target).square().mean();variance=target.flatten(0,1).var(dim=0,unbiased=False).mean() if reference_variance is None else torch.as_tensor(reference_variance,device=target.device)
    cosine=torch.nn.functional.cosine_similarity(predicted.flatten(2),target.flatten(2),dim=-1).mean()
    return {'mse':float(diff.detach()),'target_variance':float(variance.detach()),'variance_normalized_mse':float((diff/variance.clamp_min(1e-8)).detach()),'degenerate_reference':bool(variance<1e-8),'cosine':float(cosine.detach())}
