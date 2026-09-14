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

## CURRENT / LATEST STATE

- As of 2026-09-14 18:39 UTC: worker `autodl-jepa` is **running three concurrent full seed-0 pilot training jobs**, all observed past300 optimizer updates with fresh logs and no traceback/OOM/NaN matches. Live GPU97%,28,752/32,607MiB; data disk31G free.
- Immutable run SHA: `fade5b690451efd23d5e428bcf5013c0e32a8aec`. Benchmark SHA: `91886472be1263f884931b5f406d54ccd42901f5`. Later documentation commits do not change active code.
- Pixel: `pixel-s0-20260914T183511-a3085365015f`.
- Gaussian: `gaussian-s0-20260914T183511-682da9f8087f`.
- Sparse: `sparse-s0-20260914T183511-9f2f3d95bfff`.
- Worker persistent queue PID45235, launched with isolated Python `-u -m study.concurrent_pilot --authorized-full-pilot`; state `/root/autodl-tmp/robotics/jepa-worldmodel-study/runs/three-arm-pilot-queue/queue.json`. Queue-child PIDs45237/45238/45239; actual training CUDA subprocess PIDs45651/45647/45652 respectively at the check. No tmux dependency.
- Controller `jepa-pilot-monitor.service` active/running with zero restarts. Local live state `/mnt/research/jepa-worldmodel-study-storage/runs/pilot-queue.json`; monitor log `runs/pilot-monitor.log`. Read these for fresh progress instead of reusing this timestamped observation.
- Each arm:1,844,915 training windows/epoch ×2,115,308 total optimizer updates. Benchmark-based total training estimates: Pixel10h48m, Gaussian10h38m, Sparse10h49m simultaneously. Queue training makespan~10h49m from launch, plus unmeasured validation/checkpoint overhead and full common evaluation. No precise whole-queue completion time claimed.
- Latest validated result: stable three-way throughput gain and successful full-pilot startup; no full-pilot scientific results yet.
- Exact next action: let persistent training continue. After all training succeeds, queue runs common evaluation sequentially for Pixel, Gaussian and Sparse. On continue, inspect queue/manifests/logs; repair infrastructure safely, stop on scientific/code failure, preserve all artifacts and never duplicate runs.
- Pending/unknown: full-epoch sustained throughput, validation/evaluation wall time, full-pilot learning/physical metrics, final checkpoints and final result report. No other sweeps or protocol changes authorized.
