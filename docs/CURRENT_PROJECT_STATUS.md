# Current project status

Working snapshot; research history is in [CHATGPT_RESEARCH_HANDOFF.md](CHATGPT_RESEARCH_HANDOFF.md). Updated 2026-09-15 after completion and retention of the three-condition inference control.

## Scientific goal / project definition

Controlled study of temporal observation/pixel prediction versus Gaussian JEPA versus sparse JEPA for world models, initially PushT. We are testing WHETHER and WHEN JEPA helps, not assuming it must win. OGBench Cube, synthetic dynamics and potentially PDEBench are later work. This project is isolated from MARL, DA3, dehazing and old PushT projects.

## Environment and immutable baseline

- Checkout `/mnt/research/robotics/jepa-worldmodel-study`; storage `/mnt/research/jepa-worldmodel-study-storage`, both on mounted research volume. Branch `study/pixel-baseline`.
- Upstream `YilunKuang/lpworldmodel`, commit `bdd812d9432cccda8c350086006401b436f91982`; annotated tag `baseline/upstream-initial`. Origin `henry550xz/jepa-worldmodel-study`; upstream/main preserved.
- Worker `autodl-jepa`, RTX5090,32607MiB VRAM, driver595.71.05. Workspace `/root/autodl-tmp/robotics/jepa-worldmodel-study` on its50GB data disk. Dedicated `envs/lpwm-5090/bin/python`: Python3.12.3, PyTorch2.8.0+cu128, CUDA runtime12.8; base/drivers unchanged.
- Official PushT dataset SHA256 `442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08`, worker `datasets/pusht_noise`. Compatibility choices and full specifications are in manifests/conf/study and the reproduction report.

## Latest validated state and next action

The upstream reproductions, three-arm seed-0 pilot, Pixel checkpoint diagnosis and subsequent original/reencode/teacher-forced controls are complete. No active experiment queue and no training authorized. Latest report: [REENCODE_CONTROL_RESULTS.md](REENCODE_CONTROL_RESULTS.md); exact controls and failures: [REENCODE_CONTROL_PROTOCOL.md](REENCODE_CONTROL_PROTOCOL.md). Prior analysis: [PIXEL_FAILURE_ANALYSIS.md](PIXEL_FAILURE_ANALYSIS.md); pilot report: [THREE_ARM_PILOT_REPORT.md](THREE_ARM_PILOT_REPORT.md).

All three control conditions completed50 episodes with identical bank hashes and10 replans each. Original/reencode/oracle final success0/50,1/50,2/50; ever success15/50,28/50,22/50; mean regret0.00876,0.00410,0.00347; Spearman−0.076,0.173,0.454. Reencode reduces regret53.2% and improves short-horizon physical readout, but final planning success remains poor. Teacher forcing uses privileged true candidate-prefix histories and still retains the learned final-step/readout bottleneck; it is not ground-truth-cost planning.

Exact next action: review these results with the user and decide which residual bottleneck merits an explicitly authorized follow-up. Do not launch training or rerun a completed queue. Potential probe/cost/horizon/goal-retention diagnostics are recommendations only. Multi-seed generalization and causal attribution of remaining failure are unresolved; H32 has only4 episodes, and this was post-hoc reuse of test data.

## Worker and queue state

Worker `autodl-jepa` observed idle after control completion (GPU0%,2MiB used); it was not shut down. Controller `jepa-reencode-r3-monitor.service` inactive after successful retention, as expected. The control queue ended2026-09-15 18:55:04UTC (14:55:04EDT). Verify live state before any future operation; do not trust historical PIDs.

Completed worker artifact directory: project `artifacts/reencode-control-20260915-r3/`; controller mirror `/mnt/research/jepa-worldmodel-study-storage/artifacts/reencode-control-20260915-r3/`. `state.json` records completion and runtimes; `retention-verification.json` verifies all155 raw JSON/NPZ files against worker SHA256 hashes. `summary.json` and the results report contain all metrics. Control observer retains evidence but does not wake Codex. Earlier failed attempts r1/r2 and their logs are preserved; r2 horizon outputs were reused after validation, not rerun.

## Immutable provenance and retained artifacts

- Completed checkpoint training SHA `40d8c7840a0a7e96933a42e10c60a926b272430e`; control execution SHA `23083327db0c21eb1a4787e032313c7691778d06`; horizon inference SHA `1e7fbc592d1b44be09cba7a5cc00f83acc0bf3b7`. Later documentation commits do not change them.
- Frozen Pixel checkpoint/probe hashes, exact settings and invocation are in the control protocol/state. Checkpoint hash unchanged at completion; no weights or probes trained.
- Pilot final checkpoints are retained under storage `checkpoints/<run_id>/`; integrity records and run identities are in `runs/pilot-checkpoint-retention.json`. Pilot metrics/inventory: `runs/pilot-summary.json`, `runs/pilot-evaluation-artifact-inventory.json`.
- Visual diagnosis artifacts: storage `artifacts/pixel-diagnostics-20260915/` (all images, panels, physical plots, image metrics and inventory). Original reproductions and billing-interrupted attempts remain preserved.
- No remaining execution/retention blocker for the authorized control. Interpretation is a partial interface repair, not a successful planner or a definitive JEPA-versus-pixel conclusion.
