# Minimal temporal pixel baseline

## Decision and audited gradient problem
Upstream `VWorldModel._forward_adaln` reconstructs `z_emb.detach()`; concat `forward` decodes `z_pred.detach()`. Neither supplies future-pixel gradients to the encoder/dynamics. Do not equate has_decoder=True with observation prediction.

Add `study.pixel.PixelWorldModel`, a narrow VWorldModel subclass overriding only the AdaLN training forward. Preserve encoder, action Embedder, causal ARPredictor, rollout alignment and checkpoint loader contracts. Use identity link; no representation distribution regularization or latent prediction objective. Upstream files remain unchanged. Training uses the upstream Trainer through Hydra model/decoder overrides.

## Architecture and loss
Reuse ViT CLS width 384, 14-pixel patches, 12 encoder blocks, projector hidden 2048; reuse 6-layer Deep-AdaLN predictor, history 3, grouped action dimension 10. Encode only the first three images for training inputs. Predict shifted future latents at each input time, as upstream JEPA does. Feed `(B,3,1,384)` predictions directly into a new compact decoder.

Decoder proposal: linear D -> 64*7*7 grid, then five bilinear 2x upsampling + 3x3 convolution/GELU stages, channels 32,16,16,16,16, then 3-channel convolution/tanh. Output `(B*3,3,224,224)` in [-1,1], compatible with upstream normalization. No quantization, diffusion, pretrained perceptual backbone, input-image skip connection or direct access to future observations. The decoder supports power-of-two multiples of 7 for fast shape-reduced tests.

Loss is mean squared pixel error of all three future frames: predicted outputs at source offsets 0,5,10 versus true RGB offsets 5,10,15. `loss -> decoder -> predicted latent -> dynamics -> source encoder` stays connected; action embedder learns through AdaLN. Target observations are constants. There is no auxiliary reconstruction or JEPA loss in the minimal baseline. Keep teacher-forced training versus autoregressive evaluation identical across arms.

## Fairness and confounds
Pixel supervision is high-dimensional and can favor texture/background at the expense of physical state. A deterministic MSE decoder may blur multimodal futures. CLS compression might disadvantage pixels versus patch-based observation prediction; document this as the first controlled architecture, not the strongest conceivable pixel model. A patch-token extension is a later ablation.

Decoder parameters add approximately 1.25M at D=384 (exact count is recorded at model initialization); it also adds dense image compute and activations. Match backbone dimensions/data/updates first, report parameter counts and GPU time separately, and later consider matched-compute budgets. Loss scales are not directly comparable. Pixel decoder LR/init use upstream Trainer's existing muP path for the pilot, but upstream muP documentation says finite pixel readouts need special treatment whereas the implementation initializes all linear/conv weights as hidden weights. Treat the current decoder initialization as a disclosed pilot choice requiring stability checks; do not assert theoretically exact finite-output muP or fair tuned LR without evidence.

No future frame is encoded for predictor input. Tests perturb future-only images and actions, check prefix causality, check encoder/predictor/decoder gradients using pixel loss only, and require tiny-sample overfit. AdaLN-zero means action sensitivity can start at zero; test after brief training, without overriding initialization to make the test pass.

## Planning interface
Inherited rollout predicts latents with identity link. It can decode predicted futures, and frozen physical probes can read both true encodings and predicted latents through the common adapter interface. Native pixel terminal-RGB cost is available conceptually but upstream latent-CEM evaluation alone is not a fair pixel planning evaluation. Final controlled planning needs explicit shared physical-probe candidate scoring plus separately labeled native-objective planning. Simulator/checkpoint adapters remain a subsequent gate, not fabricated metrics.

## Status boundary
Design precedes implementation on study/pixel-baseline, branched only after common evaluation and deployment foundation commits. Fast NumPy/provenance checks run on the controller. Torch gradient, action, causality and overfit tests require the worker environment; no heavyweight controller installation is authorized.
