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

## CURRENT / LATEST STATE

- Full seed-0 pilot is now authorized, conditional on a bounded single-process versus three-way concurrency benchmark first. Frozen batch/config/splits/seeds/update budget and evaluation protocol must not change.
- Worker was idle at last validated audit, with31G free on data disk; no pilot run IDs or active pilot queue yet. The completed reproduction service is inactive.
- Latest validated result: PILOT_READY. Current prepared immutable run SHA: `6c70470ff0bb412b6892b2126ef4f550bfb4b6bb`; no full pilot has started.
- Exact next action: benchmark each arm alone and all three together after warmup, including loader/CPU/I/O and total VRAM. Use concurrent training only if stable and at least~20% faster in useful aggregate throughput; otherwise use the existing sequential guarded launcher. Run common evaluation after each arm; stop on scientific/code failure and preserve evidence.
- Pending: representative end-to-end throughput, concurrency benefit/stability, full evaluation time, final selected launch SHA/run IDs and pilot learning results. No additional sweeps authorized.
