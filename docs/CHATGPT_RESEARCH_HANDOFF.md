# Research handoff

Append-only research history, oldest to newest. Read [CURRENT_PROJECT_STATUS.md](CURRENT_PROJECT_STATUS.md) first for current scope and authorization. Historical instructions describe their time and do not authorize new runs.

The milestones below were migrated without changing their contents from the previous status document on 2026-09-15. Their original order is preserved; early milestone dates were not individually recorded in that document. Exact configurations and evidence are in the linked reports and manifests.

## Milestone 1 — upstream reproduction setup

Fork/remotes, clean upstream baseline, study scaffolding, code map, isolated environment and verified dataset were established. Gaussian/sparse import and forward/backward smokes passed. Reproduction snapshot `0f1720a0be0c73a98a16ce48936c052d7aaee3a6` preserved upstream scientific source. Persistent supervision replaced the original tmux monitor after an SSH launch timeout; successful experiments were not repeated.

## Milestone 2 — upstream reproduction results

| Method | Success | Training wall time | Official planning wall time |
|---|---:|---:|---:|
| Gaussian |36/50 =72%|4h33m18s|24m45s|
| Sparse |40/50 =80%|3h51m03s|24m32s|

Both used one training seed (0) and50 planning episodes (evaluation seed99). These establish executable reproduction, not a general method advantage or exact agreement with an established paper target. Both checkpoints are retained and hash-verified on controller; reproduction queue completed successfully. Full evidence: [UPSTREAM_REPRODUCTION_REPORT.md](UPSTREAM_REPRODUCTION_REPORT.md).

## Milestone 3 — common evaluator + pixel baseline readiness

Minimal temporal pixel loss propagates through decoder, predicted latent, dynamics and encoder. Shared frozen physical probes avoid comparing latent MSE across methods. Checkpoint adapters handle upstream serialization/eval quirks; simulator candidates restore by complete reset/prefix replay rather than claiming incomplete dataset state vectors are exact snapshots. Constant probe-training dimensions are masked equally for all methods. Gradient, causality, action influence and tiny-overfit checks passed; earlier failed diagnostic attempts are preserved.

## Milestone 4 — PILOT_READY

- Frozen partitions: world train17,405 / world validation512 / probe train512 / validation128 / untouched test124 / readiness fixtures4 / reserved upstream validation21. Simulator readiness/test seeds separate. See `manifests/PUSHT_PARTITIONS.json`.
- Real checkpoints, linear/MLP frozen probes, physical horizon1/2/4/8/16/32 errors, true-versus-predicted representation diagnostics, fixed-candidate ranking/order invariance and shared CEM validated.29 worker tests passed.
- FP32 batch32,8 training updates +2 validation batches; expensive upstream diagnostics disabled equally. Pixel allocated/reserved7.701/8.313GiB; Gaussian and Sparse7.810/8.131GiB. Compute-only windows/s: Pixel352.8, Gaussian304.0, Sparse308.1. These exclude loader waits/startup and are not full-epoch rates or research results.
- Training snapshot `8d8b123c6d9c05b11099ef23556f5e9159c8e424`; final evaluator `a3497a5210af0850133098ae85082231f64304f7`; prepared guarded-launch snapshot `6c70470ff0bb412b6892b2126ef4f550bfb4b6bb`.
- Readiness runs: Pixel `pixel-s0-20260914T175035-f1c2ddfbd50d`; Gaussian `gaussian-s0-20260914T175059-72dc6978657d`; Sparse `sparse-s0-20260914T175123-f919227298f8`. Compact evidence/probes/bank retained on controller; readiness checkpoints remain worker-side.
- Report: [PILOT_READINESS_REPORT.md](PILOT_READINESS_REPORT.md); frozen protocol: [PILOT_READINESS_PROTOCOL.md](PILOT_READINESS_PROTOCOL.md).16GiB+ recommended for one process at this configuration; concurrency was not yet measured at this milestone.

## Milestone 5 — concurrency benchmark and authorized pilot launch

- The representative benchmark used20 warmup updates plus60 measured seconds per solo arm and a synchronized60-second three-way interval, with loader/CPU/I/O included. Frozen config, partitions, seeds, batch32, model/optimizer settings and update budget were unchanged.
- Solo windows/s: Pixel111.08, Gaussian111.88, Sparse114.68. Three-way: Pixel94.86, Gaussian96.35, Sparse94.82; aggregate285.85 versus sequential-equivalent112.52, a154% improvement. Projected training makespan10.81h versus27.33h sequential.
- Three-way mean GPU82.7%, peak driver28,752/32,607MiB, process CPU15.91 cores; no allocator retries or OOMs. All disposable benchmark processes exited before pilot launch. Raw evidence `runs/concurrency-20260914T182614/`; report [CONCURRENCY_BENCHMARK.md](CONCURRENCY_BENCHMARK.md).
- Launch validation found that the old zero smoke-limit sentinel skipped full training. Fixed zero to mean unlimited, implementing the existing two-epoch protocol; a full-traversal regression test passed (30 worker tests total). No frozen scientific setting changed. This corrects the earlier incomplete full-path validation.
- User authorized the three-way pilot after the benchmark decision. Started all three arms together on GPU0; common evaluations wait for training to finish and then run Pixel → Gaussian → Sparse sequentially. Worker queue fails closed; controller observer retains compact evidence and never launches duplicate jobs.

## Milestone 6 — billing interruption and verified pilot restart

The user confirmed AutoDL balance exhaustion interrupted the worker on September 14. At recovery, all three original pilot processes were gone and no epoch checkpoint existed: Pixel stopped at step36,109, Gaussian35,952 and Sparse34,526, before the first epoch boundary at57,654. Original attempts are marked `interrupted_infrastructure`; logs/manifests and the archived queue are retained on worker and controller. Completed upstream reproductions and readiness artifacts are unaffected. See [PILOT_INTERRUPTION_20260914.md](PILOT_INTERRUPTION_20260914.md).

Restarted all three arms from seed0 at23:03UTC using documentation-only snapshot `40d8c7840a0a7e96933a42e10c60a926b272430e`; scientific code/configuration are unchanged from the original launch. New run IDs isolate the retries. The persistent observer now follows this snapshot. This is a fresh restart, not checkpoint continuation.

## Milestone 7 — three-arm seed-0 pilot completed and retained

All three arms completed115,308 updates under immutable SHA `40d8c7840a0a7e96933a42e10c60a926b272430e`; all three common evaluations passed execution/consistency checks. Queue finished September15 at10:38:58UTC (06:38:58EDT). Pixel training10h30m01s/evaluation20m55s; Gaussian10h41m11s/16m09s; Sparse10h29m49s/16m49s. Training was concurrent and evaluations sequential; successful queue wall time about11h35m.

Final physical-goal attainment: Pixel0/50, Gaussian6/50, Sparse1/50; ever attaining the threshold15/50,30/50,14/50 respectively. These short-horizon synthetic physical-goal tests are not the official PushT benchmark. Gaussian ranked candidates best (mean Spearman0.271 versus Pixel−0.076/Sparse−0.115); Sparse had best position probes, Pixel best angle probe. One seed and only four horizon32 episodes limit interpretation. Negative results preserved; no claim of universal JEPA superiority.

All three final checkpoints are retained on controller with SHA256 verified against worker originals. Probe weights, candidate scores, metrics and shared candidate banks are retained; all50 bank hashes match across methods. Evidence: `runs/pilot-summary.json`, `runs/pilot-checkpoint-retention.json`, `runs/pilot-evaluation-artifact-inventory.json` under durable project storage. Full comparison, commands and caveats: [THREE_ARM_PILOT_REPORT.md](THREE_ARM_PILOT_REPORT.md).

## 2026-09-15 — documentation roles separated

User directed adoption of a concise current snapshot plus append-only research history, superseding the previous combined chronological status layout. Both documents must be updated after each validated experiment or major research decision. Routine unchanged progress stays in queue state/session reports. AGENTS.md now contains durable operating rules only; worker, service, run and authorization state belongs in the current snapshot.

No experiment, configuration, artifact or scientific interpretation changed. The completed pilot and its negative results remain preserved. The next scientific action is review of [THREE_ARM_PILOT_REPORT.md](THREE_ARM_PILOT_REPORT.md); additional experiments are not authorized. No execution or retention blocker remains for that pilot.

Byte-identical pre-migration document: [archive/2026-09-15-status-before-documentation-split.md](archive/2026-09-15-status-before-documentation-split.md), SHA256 `b10ca162ab12ea7e070692a0e324fbe89f27fc34df8753e0d708857f85841037`. This archive is historical evidence, not another instruction source.

## 2026-09-15 — Pixel checkpoint failure analysis; interface confound identified

User authorized analysis of completed Pixel/Gaussian/Sparse checkpoints, explicitly without retraining. Completed new Pixel inference on all124 original held-out test episodes, horizons1/2/4/8/16/32 (counts124/124/124/124/106/4), history3, frameskip5 and recorded actions. Compared D(E(true future)), original autoregressive D(predicted latent), and teacher-forced one-step predictions. No models or probes fitted. Existing three-arm physical/probe/ranking results reused. Training SHA `40d8c7840a0a7e96933a42e10c60a926b272430e`; inference SHA `957c421d7816893f7e935b74e1263c3e9be76cbe`; runtime35.83s. Source methods, figures and all tables: [PIXEL_FAILURE_ANALYSIS.md](PIXEL_FAILURE_ANALYSIS.md). Artifacts/inventory: durable `artifacts/pixel-diagnostics-20260915/`.

Validated findings: Pixel H1 decoded block centroid error1.15 image pixels, while the latent probe reports169.83 environment-unit block RMSE. At H2 the detected block-color area is7.6% of truth, while teacher-forced centroid error remains1.05 pixels. D(E(true)) image MSE approximately0.027 versus0.0006 for teacher-forced prediction. Pixel training constrains D(P(E(history))) but not equality/compatibility of encoder and predictor latent coordinates. Rollout nevertheless reuses predicted latents as encoder-space inputs; planning applies an encoder-trained probe to those outputs. This strongly implicates feedback and readout mismatch. The decoder can generate useful one-step images; a pure capacity bottleneck and multimodal cause are unproven. Small dynamic foreground (~3%) makes global pixel MSE insensitive to object disappearance, but causal capacity waste is unresolved.

Interpretation correction: prior evaluator execution/readiness checks did not establish a scientifically valid Pixel latent-feedback/readout interface. The original negative results remain valid observations of this implementation, but cannot establish pixel-objective inferiority. Do not rewrite prior results or count this test-set diagnosis as independent confirmatory evidence. Mask-derived centroids/undirected axes are heuristic, conditional on valid detection, and separate from full physical heading probe errors. No new scientific result was fabricated for missing H32 sequences.

Decision: diagnostic request complete; no retraining or new experiment queue. Recommended next discussion is a separately authorized inference-only decode→re-encode feedback/readout control before selecting a retraining design. No execution blocker remains; attribution to multimodal blur, capacity allocation and generalized method superiority remains unresolved. Both current snapshot and research history updated.

## 2026-09-15 — inference-only decode/reencode control authorized and launched

User authorized evaluation of the existing Pixel checkpoint under original latent feedback, decode→re-encode feedback and teacher-forced one-step controls; no retraining. Frozen settings and exact oracle interpretation: [REENCODE_CONTROL_PROTOCOL.md](REENCODE_CONTROL_PROTOCOL.md). Reuse124 held-out episodes,50 candidate banks, frozen saved probe, CEM64/8/5 with horizon5, execute1 and10 replans. Teacher forcing in CEM uses true candidate-prefix simulator history; this is privileged diagnostic information and its results cannot be labeled model-only planning.

Started corrected immutable inference snapshot `1e7fbc592d1b44be09cba7a5cc00f83acc0bf3b7`, run folder `reencode-control-20260915-r2`, under a project flock and detached process; controller observer retains results. The first attempt stopped before planning on a tight causal-prefix numerical consistency check (max difference0.044 physical units). Action encoding now uses only the causal prefix to prevent future-length-dependent numerics; no tolerance relaxation. Failed logs/state retained. Observer inventory syntax fixed before verified monitoring; no training or completed evaluation was repeated by that observer.

Decision: continue the authorized inference queue, quantify repair once all conditions finish, and update both documents with validated results. No additional training authorized. Current progress, process identity and artifact paths are in the working snapshot/live state; no final repair claim is made at launch.

## 2026-09-15 — control horizons validated; planning comparison advancing

All124 open-loop controls completed under inference SHA `1e7fbc592d1b44be09cba7a5cc00f83acc0bf3b7`. A JSON integer/string horizon-key bug then stopped baseline comparison before planning. Corrected active SHA `23083327db0c21eb1a4787e032313c7691778d06` reuses those outputs after hash/protocol checks; original physical metrics now verified against prior pilot. No horizon rerun or training. Both failed startup attempts preserved.

Validated block-position RMSE original/reencode/teacher-forced: H1 169.83/39.02/39.02; H2 143.98/41.82/42.27; H4 131.38/49.44/44.73; H8 118.54/61.11/41.75; H16 94.92/76.67/34.69; H32 41.34/88.98/19.07. Same cohorts, only4 episodes at H32. H1 improvement demonstrates compatible readout, not feedback repair; later horizons combine both changes. Long-horizon accumulation remains. Planning repair is not yet established.

Active folder `reencode-control-20260915-r3`; observer `jepa-reencode-r3-monitor.service`. Original50-episode recomputation advancing, followed automatically by reencode and privileged teacher-forced oracle. Next authorized action is finish and validate this comparison; no training until results are understood and separately authorized. Intermediate tables in the artifact folder’s SUMMARY.md; regenerate with `study.summarize_reencode` as stages complete. Full settings and failures in [REENCODE_CONTROL_PROTOCOL.md](REENCODE_CONTROL_PROTOCOL.md).

## 2026-09-15 — original and reencode planning controls completed

Validated50 episodes each,10 replans and matching candidate-bank hashes under the unchanged control protocol. Original/reencode mean ranking regret0.00876/0.00410 (~53% reduction), mean Spearman−0.076/+0.173, final success0/50 versus1/50, ever success15/50 versus28/50. Runtime349.68s/748.48s. Original reproduces the prior pilot outcomes. This supports a partial interface repair with substantially better ranking, but final goal success remains poor; no claim of a complete repair.

Teacher-forced privileged oracle remains active (3/50 completed at check, approximately394s/episode); simulating candidate prefixes makes it much slower than model-only planning. Queue/monitor healthy, artifacts retained incrementally in `artifacts/reencode-control-20260915-r3/`; no retraining. Next authorized action is finish this oracle and quantify the full comparison before any training decision. Partial oracle results are not final evidence. No protocol or resource-limit changes made.

## 2026-09-15 — full frozen inference control completed and hash-verified

All150 planning episodes completed at18:55:04UTC (14:55:04EDT), with no retraining. Final original/reencode/teacher-forced-oracle results: mean regret0.00876/0.00410/0.00347; Spearman−0.076/0.173/0.454; final success0/50,1/50,2/50; ever success15/50,28/50,22/50. Reencode improves regret53.2% and ever attainment26 percentage points, but final success only2 points. Teacher-forced true prefixes improve ranking further without solving goal retention. These are physical-goal diagnostics, not official PushT coverage success. No general method-superiority claim follows.

Original/reencode/oracle stage runtimes349.68s/748.48s/21128.88s. Original metrics/candidate costs reproduce retained pilot values; every condition has50 matching candidate-bank hashes and10 replans each. All155 raw worker JSON/NPZ artifacts have matching controller SHA256 hashes in `artifacts/reencode-control-20260915-r3/retention-verification.json`. Checkpoint/probe frozen; final checkpoint hash unchanged. Execution SHA `23083327db0c21eb1a4787e032313c7691778d06`, reused horizon inference SHA `1e7fbc592d1b44be09cba7a5cc00f83acc0bf3b7`. Reports: [REENCODE_CONTROL_RESULTS.md](REENCODE_CONTROL_RESULTS.md), [REENCODE_CONTROL_PROTOCOL.md](REENCODE_CONTROL_PROTOCOL.md).

Conclusion: readout/feedback compatibility accounts for part of the original Pixel failure, but residual probe geometry, cost/horizon design and goal retention remain unresolved causes. Even the oracle retains learned final prediction/readout; it is not an upper bound from perfect physical-state cost. Single-seed post-hoc analysis and four H32 episodes remain limitations. Preserve the original and corrected negative results.

Decision: authorized inference goal complete, worker idle and observer exited; no training or new queue launched. Next action is user review and explicit authorization of any follow-up diagnostic/training design. Current snapshot replaced with completion state and authoritative artifact links; no execution/retention blocker remains.

## 2026-09-15 — four-arm mechanism gates implemented; compute/theory gates remain open

User authorized implementation and bounded validation of standard Pixel, free-running rollout-reconstruction Pixel, Pixel+JEPA-style latent consistency and Gaussian JEPA, prohibiting full runs before the gate. Implemented shared ViT384/AdaLN/decoder architecture, seed0, batch32 FP32, history3/frameskip5,6-frame windows and3 common future targets. Draft consistency coefficient1.0, online non-detached latent targets; Gaussian RDMReg weight0.5. Free-running gradients traverse predicted-latent feedback without detachment. Gaussian decoder is instantiated identically but dormant. Full objective and information distinctions: [MECHANISM_EXPERIMENT_PROTOCOL.md](MECHANISM_EXPERIMENT_PROTOCOL.md).

All14 bounded tests passed, all4 real training smokes (8 updates+2 validation batches) passed, and all4 common evaluator smokes passed (4 readiness episodes, horizons1/2/4/8/16/32,1 candidate bank,2 replans). Temporal alignment closure and Pixel-specific decode/reencode cycle closure are explicit metrics; Gaussian random-decoder cycle is not applicable. Physical readout is compatible E(D(pred)) for each Pixel arm and aligned latent for Gaussian, with original latent feedback retained in every arm. No research result is inferred from8-update checkpoints.

Training snapshot `1ab94751e93e5f0e73cdab775db3400406323b9f`; evaluator snapshot `0e7c3f69f68f2d09c36654fa96d3876468092bb4`. Same initial weights, parameter counts and first batch hashes verified. Pixel/rollout/consistency/Gaussian compute-only windows/s222.4/296.7/199.7/207.7; allocated/reserved GiB11.24/12.46,7.77/8.41,12.88/14.08,11.36/11.90. Exact compute equality is false, and intermediate conditioning differs by the intended teacher-forcing intervention. Audit: [MECHANISM_READINESS_AUDIT.md](MECHANISM_READINESS_AUDIT.md); retained per-run evidence and hashes indexed by storage `runs/mechanism-smokes-20260915-r2/`. Smoke checkpoints remain disposable worker artifacts; earlier research checkpoints untouched.

Preserved failures: consistency synthetic80-update pixel-overfit criterion did not pass; extending equally to300 updates passed without loss-weight/criterion tuning. First compatible-readout evaluator failed a numerical prefix check; fixed causal-prefix/per-step batching across all arms without relaxing tolerances or retraining. Initial encoder forward hook missed upstream direct.forward calls; source-derived workload counts labeled honestly and instrumentation corrected for future use.

Separately implemented a provisional linear-Gaussian rank-one state+nuisance simulation: beta is nuisance amplitude, rho nuisance persistence, relevant-state alpha0.8. Candidate pixel boundary beta*abs(rho)=abs(alpha); fixed-whitened-target reference boundary abs(rho)=abs(alpha), not a learned JEPA theorem.25 cells CPU-only (10k train/20k test pairs per cell),3 tests passed,43/43 away-from-boundary cases agreed. [LINEAR_GAUSSIAN_PROVISIONAL.md](LINEAR_GAUSSIAN_PROVISIONAL.md) records equations and caveats; artifacts in storage `artifacts/linear-gaussian-provisional-20260915/`. User's intended beta/rho theory definitions were requested but not provided, so exact correspondence is unresolved.

Decision: bounded implementation validated; full-run gate remains closed pending compute/information interpretation and frozen budget design. No full runs or new active GPU queues. Next action is obtain the intended theory equations and review the concrete audit; no training launch until separately authorized after gates are resolved. Both current snapshot and history updated without rewriting earlier findings.
