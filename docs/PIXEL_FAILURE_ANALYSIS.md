# Why the seed-0 Pixel model failed: checkpoint diagnostics

## Main finding

The strongest supported explanation is an incompatible latent feedback and readout interface in this Pixel baseline. It learns useful one-step images, but predicted latents are not constrained to inhabit the encoder representation space. Feeding them back into a predictor trained on encoder latents causes rapid rollout failure. Applying an encoder-trained physical probe directly to predicted latents also gives a misleading readout of otherwise useful one-step images. These are baseline/interface limitations, not evidence that observation prediction inherently loses to JEPA.

No model or probe was retrained. Original scientific results remain unchanged. New Pixel inference uses the same124 held-out test episodes and original horizon alignment; existing three-checkpoint physical/probe/ranking results are reused. This is post-hoc diagnostic use of the test set, not a fresh confirmatory test for future changes.

## Evidence and provenance

- Training SHA `40d8c7840a0a7e96933a42e10c60a926b272430e`; new inference SHA `957c421d7816893f7e935b74e1263c3e9be76cbe`.
- Checkpoint identities and hashes: durable `runs/pilot-checkpoint-retention.json`; run IDs and configs: [THREE_ARM_PILOT_REPORT.md](THREE_ARM_PILOT_REPORT.md).
- Raw images, metrics, image-summary.json, physical plots and diagnostic scripts: `/mnt/research/jepa-worldmodel-study-storage/artifacts/pixel-diagnostics-20260915/`.
- Inference: `study/diagnose_pixel.py`; image aggregation: `study/summarize_pixel_diagnostics.py`; physical plots: `study/plot_pixel_diagnostics.py`.
- Each horizon is5 simulator steps. Same initial observation history at frames0/5/10 and recorded future actions. H1/2/4/8 have124 episodes, H16 has106, H32 only4. No missing horizons fabricated. Teacher forcing is explicitly a diagnostic using fresh true history, not a deployable open-loop result.

## 1. Physical prediction error versus horizon

All methods use frozen linear probes fit on their true-observation encodings. Entries are pusher RMSE / block RMSE / wrapped block-angle MAE (position in environment units, angle in radians). These are physical readouts of latent rollout, not pixel MSE. Pixel predicted-latent probe compatibility is compromised, as demonstrated below, so these values must not be interpreted as direct image-object accuracy.

| Horizon | N | Pixel | Gaussian | Sparse |
|---|---:|---|---|---|
|1|124|213.02/169.83/1.57|34.11/39.42/1.20|61.27/40.28/1.19|
|2|124|207.03/143.98/1.57|32.73/39.27/1.16|59.08/40.03/1.12|
|4|124|178.49/131.38/1.27|32.29/37.78/1.06|56.79/38.38/1.03|
|8|124|163.88/118.54/1.02|28.42/35.93/0.74|56.94/38.20/0.70|
|16|106|168.39/94.92/0.62|25.97/47.83/0.44|56.18/54.78/0.51|
|32|4|179.63/41.34/0.30|26.09/24.98/0.40|51.76/52.54/0.34|

True-future encoding probe error, same cohorts (representation-only diagnostic):

| Horizon | Pixel | Gaussian | Sparse |
|---|---|---|---|
|1|91.83/39.54/0.36|31.83/39.60/1.17|27.90/35.24/0.84|
|2|96.72/40.58/0.41|30.33/39.20/1.16|26.27/34.25/0.83|
|4|85.35/46.02/0.51|28.89/36.98/1.04|24.26/32.08/0.73|
|8|78.70/42.55/0.43|25.65/30.81/0.71|24.81/29.42/0.53|
|16|66.73/35.18/0.39|19.93/21.61/0.39|18.78/20.53/0.34|
|32|16.72/22.18/0.26|16.57/6.86/0.08|20.77/8.36/0.11|

[Physical error plot](/mnt/research/jepa-worldmodel-study-storage/artifacts/pixel-diagnostics-20260915/physical-error-horizons.png), with PDF alongside it. RMSE is pooled by square root of mean per-episode squared RMSE; angle errors are averaged. Changes across horizons partly reflect different future states and, at16/32, different cohorts; decreasing aggregate errors do not establish improving dynamics.

## 2. Visual rollouts

Panels contain four rows: ground truth; `D(E(true future))`; `D(predicted future latent)` using the original autoregressive feedback; teacher-forced one-step prediction with fresh true history. Columns are1/2/4/8/16/32 where available. Deterministic selection: first two test episodes and all four episodes long enough for32, without selecting on outcome.

- [panel-ep11336](/mnt/research/jepa-worldmodel-study-storage/artifacts/pixel-diagnostics-20260915/panel-ep11336.png)
- [panel-ep16233](/mnt/research/jepa-worldmodel-study-storage/artifacts/pixel-diagnostics-20260915/panel-ep16233.png)
- [panel-ep16505](/mnt/research/jepa-worldmodel-study-storage/artifacts/pixel-diagnostics-20260915/panel-ep16505.png)
- [panel-ep17790](/mnt/research/jepa-worldmodel-study-storage/artifacts/pixel-diagnostics-20260915/panel-ep17790.png)
- [panel-ep2932](/mnt/research/jepa-worldmodel-study-storage/artifacts/pixel-diagnostics-20260915/panel-ep2932.png)
- [panel-ep8523](/mnt/research/jepa-worldmodel-study-storage/artifacts/pixel-diagnostics-20260915/panel-ep8523.png)

Visual inspection of episodes16505 and2932 shows recognizable blocks in one-step and teacher-forced predictions, but near disappearance under autoregressive feedback from horizon2. Static goal/background persist. Direct decoding of true encodings produces unrelated shapes. This is more severe than slightly blurred edges.

## 3. Pixel image error and sharpness

RGB image MSE on [0,1], before PNG quantization. Edge energy is the mean squared adjacent-pixel difference horizontally plus vertically; table shows energy divided by the corresponding ground-truth energy, averaged over episodes. Whole-image sharpness includes the static goal/border: reduced energy can mean blur OR missing objects; it is not a standalone test for multimodality.

| H | D(E true) MSE | Rollout MSE | Teacher-forced MSE | Rollout edge ratio | Teacher-forced edge ratio | Rollout block area / truth |
|---|---:|---:|---:|---:|---:|---:|
|1|0.026587|0.000649|0.000649|0.624|0.624|1.026|
|2|0.026899|0.005210|0.000648|0.453|0.620|0.076|
|4|0.026369|0.005066|0.000648|0.462|0.594|0.068|
|8|0.026164|0.004701|0.000728|0.477|0.571|0.081|
|16|0.027236|0.004298|0.000669|0.486|0.579|0.089|
|32|0.020775|0.003485|0.000383|0.514|0.606|0.070|

### Image-derived block pose

A fixed gray-blue color mask isolates block-colored pixels. Centroid is mask centroid in224×224 image pixels; orientation is the undirected PCA axis modulo pi, compared with the same estimator on ground truth. This supplementary image-space orientation is NOT full signed physical heading; full physical heading errors are in section1. Masks require25 pixels, area0.1–3 times truth, and eigenvalue anisotropy>0.05. Thresholds are heuristic, not a separately calibrated detector. Hallucinated components can pass; missing blocks cannot be assigned a meaningful angle. Report invalid detections rather than substituting zero. Errors below are conditional on valid masks and must be read with valid counts; they are not unconditional pose accuracy.

| H | Rollout valid / N | Rollout centroid px | Rollout axis rad | Teacher-forced valid / N | Teacher centroid px | Teacher axis rad |
|---|---|---:|---:|---|---:|---:|
|1|124/124|1.15|0.135|124/124|1.15|0.135|
|2|40/124|72.98|0.732|123/124|1.05|0.111|
|4|38/124|55.43|0.694|124/124|1.16|0.063|
|8|45/124|49.61|0.787|124/124|1.41|0.090|
|16|38/106|43.72|0.758|106/106|1.26|0.094|
|32|1/4|46.39|1.433|4/4|1.07|0.066|

At H1, decoded block position is good despite a169.83-unit block RMSE from the latent physical probe. At H2, block-color area drops from1.026 to0.076 of truth and the one-step teacher-forced control remains accurate. Thus failure cannot be explained solely by insufficient decoder resolution.

Dynamic foreground (gray-blue block plus blue pusher) occupies about3% of pixels. At H2 rollout foreground MSE is about0.158 versus white-background MSE about0.0003. Full-image averaging hides large errors on small moving objects. This supports an objective-weighting concern, not proof of wasted model capacity; no capacity allocation or saliency experiment was performed.

## 4. Decoder/input-space mismatch versus dynamics

`PixelWorldModel._forward_adaln` in `study/pixel.py` trains only `D(P(E(history), actions))` against next images. It neither trains `D(E(image))` nor aligns the predictor output with `E(future)`. The returned predicted latent can use a different coordinate system from the encoder latent while achieving low pixel loss. `VWorldModel._rollout_adaln` in `models/visual_world_model.py` nevertheless feeds that output back as if it were an encoded observation. `CheckpointAdapter.predict_states` in `study/adapters.py` also passes it directly to a probe fit on true encodings by `study/readiness_eval.py`.

The diagnostic controls support two distinct issues:

1. **Feedback mismatch:** teacher-forced images stay useful but autoregressive images fail after the first feedback step. This is consistent with distribution shift between predicted and encoded latents. It is not just a long-horizon error accumulation story: collapse begins at H2.
2. **Probe/readout mismatch:** good H1 image geometry coexists with very poor predicted-latent physical readout. An encoder-trained probe is not validated for an unconstrained Pixel predictor output. Same evaluator code is not sufficient to guarantee a fair interface across objectives.

`D(E(true))` has MSE about0.027 versus about0.0006 for teacher-forced prediction, but this is an untrained composition. It cannot isolate decoder capacity. The correct conclusion is incompatibility of the two latent usages; a pure decoder bottleneck remains unproven. The successful teacher-forced control argues against a gross inability of the decoder to represent the scene.

## 5. Probes, decisions and final goals

| Method | Linear probe pusher/block/angle | MLP probe pusher/block/angle | Mean candidate regret | Mean Spearman | Final goal /50 | Ever goal /50 |
|---|---|---|---:|---:|---:|---:|
|pixel|88.14/36.75/0.36|75.24/19.96/0.15|0.00876|-0.076|0|15|
|gaussian|30.56/29.96/0.70|21.92/25.44/0.44|0.00415|0.271|6|30|
|sparse|26.22/27.03/0.53|15.41/19.30/0.25|0.01030|-0.115|1|14|

Gaussian is best in this planner; Sparse has better position probes and Pixel better angle probes. These are synthetic reachable physical goals from a fixed initial simulator state, not official PushT coverage success. Pixel candidate rankings combine rollout failure and an incompatible probe interface; they do not establish that a correctly interfaced pixel planner would fail.

## 6. Supported explanations

| Explanation | Assessment |
|---|---|
| Multimodal blur | Blur/soft edges are observed, but multimodality is **unresolved**. No conditional-mode analysis was done. Abrupt block disappearance under latent feedback is better supported than averaging multiple possible futures. |
| Wasted capacity on irrelevant pixels | Dominance of static/background pixels in the loss is supported descriptively. Causal capacity waste is **unresolved** without a controlled ablation. |
| Compounding dynamics error | **Supported operationally:** H2 feedback causes a large error jump, while fresh true-history controls remain accurate. More specifically, incompatible autoregressive latent feedback is strongly implicated. |
| Poor decision-relevant geometry | **Supported for the deployed representation/readout interface**, especially pusher probes and predicted-latent readout; not evidence that one-step decoded images lack block geometry. |
| Decoder bottleneck | Not established. The decoder can make useful teacher-forced images; D(E) tests an untrained composition. |
| General Pixel versus JEPA superiority claim | **Unresolved.** This baseline has a substantive interface confound and one training seed. The pilot cannot cleanly attribute the decision gap to the scientific objective alone. |

Recommended next decision, not authorization: design an inference-only decode→re-encode feedback/readout control and a validated observation-space physical readout before considering retraining. If a new training baseline is chosen, specify how predicted state remains compatible with recurrent inputs without silently adding the JEPA objective. Do not alter completed results. No retraining or new research sweep was launched.
