import pytest
torch=pytest.importorskip('torch')
from torch import nn
from models.vit_encoder import ViTEncoder
from models.infojepa_modules import ARPredictor,Embedder,Link,RDMReg
from study.pixel import PixelDecoder
from study.mechanism import MechanismWorldModel,ARMS,latent_closure

def model(arm):
 torch.set_num_threads(1);torch.manual_seed(11)
 return MechanismWorldModel(image_size=28,num_hist=3,num_pred=3,training_horizon=3,mechanism=arm,encoder=ViTEncoder(image_size=28,patch_size=14,dim=16,depth=1,heads=2,dim_head=8,mlp_dim=32,proj_hidden=32,proj_dim=16),proprio_encoder=nn.Identity(),action_encoder=Embedder(in_chans=10,emb_dim=16),predictor=ARPredictor(num_frames=3,depth=1,heads=2,dim_head=8,mlp_dim=32,input_dim=16,hidden_dim=16,pred_proj_hidden=32,dropout=0),decoder=PixelDecoder(16,28,16),train_encoder=True,train_predictor=True,train_decoder=True,action_conditioning='adaln',action_dim=16,link=Link('identity'),regularizer=RDMReg(target_p=2,num_projections=32,agg='b'),reg_weight=.5,detach_target=False)

def batch():
 torch.manual_seed(3);obs={'visual':(torch.rand(4,1,3,28,28)*.6-.3).repeat(1,6,1,1,1),'proprio':torch.zeros(4,6,4)};return obs,torch.randn(4,6,10)

@pytest.mark.parametrize('arm',ARMS)
def test_shapes_gradients_and_causality(arm):
 m=model(arm);obs,act=batch();pred,im,_,loss,_=m(obs,act);assert pred.shape==(4,3,1,16);loss.backward()
 for name in ['encoder','predictor']+([] if arm=='gaussian' else ['decoder']):assert sum(float(p.grad.abs().sum()) for p in getattr(m,name).parameters() if p.grad is not None)>0
 m.eval();changed={k:v.clone() for k,v in obs.items()};changed['visual'][:,-1]+=10
 torch.testing.assert_close(m(obs,act)[0],m(changed,act)[0])
 changed['visual'][:,3:]+=10
 torch.testing.assert_close(m(obs,act)[0][:,:1],m(changed,act)[0][:,:1])
 if arm=='pixel_rollout':torch.testing.assert_close(m(obs,act)[0],m(changed,act)[0])

@pytest.mark.parametrize('arm',ARMS)
def test_action_and_overfit(arm):
 m=model(arm);obs,act=batch();opt=torch.optim.Adam(m.parameters(),lr=.002);key='latent_loss' if arm=='gaussian' else 'pixel_loss';before=float(m(obs,act)[4][key].detach())
 for _ in range(5):opt.zero_grad();m(obs,act)[3].backward();opt.step()
 assert (m(obs,act)[0]-m(obs,act.flip(0))[0]).abs().max()>1e-7
 for _ in range(295):opt.zero_grad();m(obs,act)[3].backward();opt.step()
 assert float(m(obs,act)[4][key].detach())<before*.8

def test_free_running_last_loss_reaches_first_prediction():
 m=model('pixel_rollout');obs,act=batch();calls=[]
 def hook(module,args,out):out.retain_grad();calls.append(out)
 handle=m.predictor.register_forward_hook(hook);images=m(obs,act)[1];images[:,-1].square().mean().backward();handle.remove();assert len(calls)==3;assert calls[0].grad is not None and calls[0].grad.abs().sum()>0

def test_consistency_target_receives_gradient():
 m=model('pixel_consistency');obs,act=batch();obs['visual'].requires_grad_(True);m(obs,act)[4]['latent_loss'].backward();assert obs['visual'].grad[:,-1].abs().sum()>0

def test_closure_identity_and_collapse_flag():
 z=torch.randn(4,3,1,16);assert latent_closure(z,z)['mse']==0;assert latent_closure(torch.zeros_like(z),torch.zeros_like(z))['degenerate_reference']
