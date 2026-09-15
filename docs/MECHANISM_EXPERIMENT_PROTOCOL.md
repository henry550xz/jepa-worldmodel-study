# Four-arm mechanism experiment — draft readiness gate

No full training is authorized or launched. Scope: implement and validate seed-0 PushT configurations and audit information/compute; separately implement a cheap linear-Gaussian theory scaffold. Configuration: `conf/study/mechanism.json`. Training entry point provided here is bounded to8 updates and2 validation batches; there is deliberately no full-run switch.

## Objectives and shared settings

Shared ViT384, AdaLN predictor/action encoder, identity link, decoder architecture, muP initialization/AdamW lr1e-4, FP32 batch32, history3, frameskip5, frozen episode partitions,6-frame windows and3 common future target times. Seed0 and chronological/window order match. Each pixel objective averages MSE across those3 target images. Draft horizon3 and auxiliary coefficient1 are declared choices, not tuned on evaluation outcomes or implied user theory parameters.

| Arm | Training context | Objective |
|---|---|---|
| Standard Pixel | Sliding true3-frame history for each next-step target | Mean future-image MSE |
| Rollout-reconstruction Pixel | Initial true3-frame history; subsequent inputs are predicted latents | Mean3-step future-image MSE; untruncated backpropagation through latent feedback |
| Pixel + latent consistency | Same teacher forcing as Standard Pixel | Image MSE +1.0 × predicted-latent/encoded-future MSE |
| Gaussian JEPA | Same teacher forcing | Latent MSE +0.5 × upstream Gaussian RDMReg |

Latent targets are online and not detached, matching the existing upstream Gaussian configuration (`detach_target=false`); no new EMA/target network. The auxiliary arm has no Gaussian regularizer, so it isolates adding alignment to Pixel rather than changing two losses. Gaussian regularization uses all6 encoded frames. Source: `study/mechanism.py`.

Standard Pixel here is the same one-step teacher-forced objective family, evaluated on3 full-context transitions per common6-frame window. It is NOT a byte-identical rerun of the earlier4-frame pilot, whose3 parallel targets had histories of varying effective length. No earlier results are substituted as matched new-arm results.

## Information and compute audit

All arms receive the same external sequences/actions, same future target timestamps and number of windows. No predictor sees its target or later observations. Teacher forcing uses true intermediate history for later predictions; free running deliberately does not. This is the intervention, not a claim that intermediate conditioning information is identical. State labels are not supplied to world-model training.

Identical world-model architecture and total instantiated parameters do not imply identical active parameters or FLOPs. Gaussian instantiates the same decoder to preserve architecture/init comparison, but it is dormant and untrained; its random output must not be evaluated as a trained observation decoder. Other arms train it. Gaussian adds distribution matching; the consistency arm adds target encoding; free running adds recurrent backward dependencies. Instrumentation records module frame/token workloads, peak memory, throughput and gradients. Gaussian decoder gradients are intentionally absent, not a missing-gradient bug.

Matched-update/window training is a defensible primary mechanism comparison with measured cost reporting, but it is NOT compute-matched. Equal wall-clock/FLOP budget and equal update/data exposure generally cannot both be enforced when objectives differ without wasting compute or changing exposure. Do not pad with useless operations and claim fairness. Full-run gate remains blocked until the resource-budget interpretation and these information differences are explicitly reviewed. No cost-equivalence claim based merely on batch size or architecture is permitted.

## Evaluation and closure

Reuse the frozen common physical metrics, partitions and planning settings from `conf/study/pilot.json`: horizons1/2/4/8/16/32 as sequence length permits; fixed candidate banks; separate final/ever physical-goal attainment; horizon5, execute1,10 replans, CEM64/8/5. Use the same train-only probe fitting and validation selection. For all pixel arms the primary readout is frozen E(D(predicted latent))→probe, avoiding the known arbitrary latent-readout mismatch. Gaussian uses its aligned latent→probe. Keep original latent feedback in all arms so the training mechanism is tested, rather than silently applying inference reencode feedback. Report raw latent diagnostics separately; do not select readouts per arm based on test performance. Equal CEM counts do not imply equal planning wall time.

Temporal latent closure/alignment is `mean((z_pred − E(o_true_future))²)`, with cosine and target-variance-normalized MSE, reference variance and a degenerate-reference flag. It combines representational compatibility with dynamics prediction; it is not an isolated manifold-distance test. Report raw values within an arm, not as cross-method physical performance. Evaluation normalization uses the stated true-encoding reference cohort; no fitted probe/model sees test labels.

Bounded common-evaluator smokes use only existing readiness fixtures/seeds, not new held-out scientific test selection. No fake planning success threshold: readiness checks plumbing, shapes, finiteness, action sensitivity and provenance, not favorable scientific scores. Full-run evaluation requires the same declared protocol without simulator oracle prefixes.

## Gates and known limitations

Tests cover shapes, gradients, no target leakage, action conditioning after initialization, equal-budget tiny overfit, free-running gradient through earlier predictions, target-gradient semantics and closure identity/collapse flags. First80-step synthetic overfit check failed Pixel+consistency's20% pixel-loss reduction criterion; failure retained. Extended all arms equally to300 synthetic updates without changing the loss weight or criterion; this is a bounded plumbing check, not a research hyperparameter search. Report actual results before marking gates passed.

Real-architecture/data smokes:8 batch32 updates +2 validation batches, checkpoints, resolved configs and telemetry per arm. Verify shared initial module hashes, first data batch hash, module parameter counts and costs. Evaluation smoke implementation: `study/mechanism_evaluate.py`; full evaluation/launch is not authorized by a successful smoke.


Pixel arms additionally report cycle closure `mean((z_pred − E(D(z_pred)))²)` and cosine with the same declared normalization reference. Gaussian cycle closure is explicitly not applicable because its decoder is dormant/untrained; never fabricate a zero or interpret a random-decoder cycle as an objective comparison. The shared temporal alignment metric is available for every arm. Both quantities are diagnostics, not direct physical performance scores.

All four training smokes and all four common-evaluator smokes passed; see [MECHANISM_READINESS_AUDIT.md](MECHANISM_READINESS_AUDIT.md). First evaluator attempt stopped on a horizon-prefix numerical consistency assertion. Revised evaluator uses causal action-prefix encoding and fixed per-step readout shapes for every arm; it does not loosen the tolerance or feed reencoded predictions back into the dynamics. Failed artifacts preserved. Common smoke probes use readiness train/validation/fixture selections and identical candidate banks.

The consistency arm directly optimizes temporal latent alignment, so a smaller alignment metric is not independent evidence of better physical prediction or control. Physical and decision metrics remain the scientific outcomes. Normalized closure can be very large for nearly constant smoke encodings; report reference variance/cosine and do not hide that with scale clipping or declare a learned representation from eight updates.
