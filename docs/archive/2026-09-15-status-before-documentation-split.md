# Current project status

## Scientific goal / project definition

Controlled study of temporal observation/pixel prediction versus Gaussian JEPA versus sparse JEPA for world models, initially PushT. We are testing WHETHER and WHEN JEPA helps, not assuming it must win. OGBench Cube, synthetic dynamics and potentially PDEBench are later work. This project is isolated from MARL, DA3, dehazing and old PushT projects.

## Environment and immutable baseline

- Checkout `/mnt/research/robotics/jepa-worldmodel-study`; storage `/mnt/research/jepa-worldmodel-study-storage`, both on mounted research volume. Branch `study/pixel-baseline`.
- Upstream `YilunKuang/lpworldmodel`, commit `bdd812d9432cccda8c350086006401b436f91982`; annotated tag `baseline/upstream-initial`. Origin `henry550xz/jepa-worldmodel-study`; upstream/main preserved.
- Worker `autodl-jepa`, RTX5090,32607MiB VRAM, driver595.71.05. Workspace `/root/autodl-tmp/robotics/jepa-worldmodel-study` on its50GB data disk. Dedicated `envs/lpwm-5090/bin/python`: Python3.12.3, PyTorch2.8.0+cu128, CUDA runtime12.8; base/drivers unchanged.
- Official PushT dataset SHA256 `442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08`, worker `datasets/pusht_noise`. Compatibility choices and full specifications are in manifests/conf/study and the reproduction report.

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

## CURRENT / LATEST STATE

- Authorized seed-0 pilot is **complete**, including training, common evaluation, output validation, final checkpoint retention and comparison report. No active experiment queue or next experiment is authorized.
- Worker `autodl-jepa` observed idle September15 11:35UTC, GPU0%,2MiB used, data disk27GB free. Worker was not shut down; it may still incur rental charges. Controller monitor exited successfully (exit0) after queue completion; inactive is expected. Verify live state before future operations.
- Immutable completed run SHA: `40d8c7840a0a7e96933a42e10c60a926b272430e`; later documentation commits do not alter it.
- Pixel `pixel-s0-20260914T230335-3649012fd387`; Gaussian `gaussian-s0-20260914T230335-40a3cf2cc7af`; Sparse `sparse-s0-20260914T230335-6f99643d9771`.
- Completed queue evidence: controller `/mnt/research/jepa-worldmodel-study-storage/runs/pilot-queue.json`; worker `runs/three-arm-pilot-queue/queue.json`. Do not restart this completed queue or reuse its recorded PIDs. Per-run training manifests say `training_complete`; separate evaluation metrics say `passed`, and queue says `complete`.
- Latest validated result: complete matched pilot with mixed scientific outcomes, documented above and in the report. `passed` describes evaluator completion, not favorable scientific performance.
- Exact next action: review the report with the user; await authorization for any additional experiment or changed protocol. Recommended discussion: weak Pixel predicted-state decoding, negative Sparse candidate ranking, goal retention, and broader simulator coverage. These recommendations do not authorize runs.
- Pending/unknown: multi-seed generalization, broader simulator initial-state coverage, full-run average GPU utilization, and any future follow-up protocol. No remaining execution/retention blocker for this pilot. Billing-interrupted attempts and upstream reproductions remain preserved.
