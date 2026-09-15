# Current project status

Working snapshot; research history is in [CHATGPT_RESEARCH_HANDOFF.md](CHATGPT_RESEARCH_HANDOFF.md). Updated 2026-09-15 after completed checkpoint-only Pixel diagnostics; prior worker observations below retain their original timestamps.

## Scientific goal / project definition

Controlled study of temporal observation/pixel prediction versus Gaussian JEPA versus sparse JEPA for world models, initially PushT. We are testing WHETHER and WHEN JEPA helps, not assuming it must win. OGBench Cube, synthetic dynamics and potentially PDEBench are later work. This project is isolated from MARL, DA3, dehazing and old PushT projects.

## Environment and immutable baseline

- Checkout `/mnt/research/robotics/jepa-worldmodel-study`; storage `/mnt/research/jepa-worldmodel-study-storage`, both on mounted research volume. Branch `study/pixel-baseline`.
- Upstream `YilunKuang/lpworldmodel`, commit `bdd812d9432cccda8c350086006401b436f91982`; annotated tag `baseline/upstream-initial`. Origin `henry550xz/jepa-worldmodel-study`; upstream/main preserved.
- Worker `autodl-jepa`, RTX5090,32607MiB VRAM, driver595.71.05. Workspace `/root/autodl-tmp/robotics/jepa-worldmodel-study` on its50GB data disk. Dedicated `envs/lpwm-5090/bin/python`: Python3.12.3, PyTorch2.8.0+cu128, CUDA runtime12.8; base/drivers unchanged.
- Official PushT dataset SHA256 `442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08`, worker `datasets/pusht_noise`. Compatibility choices and full specifications are in manifests/conf/study and the reproduction report.

## Latest validated state and next action

- Authorized seed-0 pilot is **complete**, including training, common evaluation, output validation, final checkpoint retention and comparison report. No active experiment queue or next experiment is authorized.
- Worker `autodl-jepa` observed idle September15 11:35UTC, GPU0%,2MiB used, data disk27GB free. Worker was not shut down; it may still incur rental charges. Controller monitor exited successfully (exit0) after queue completion; inactive is expected. Verify live state before future operations.
- Immutable completed run SHA: `40d8c7840a0a7e96933a42e10c60a926b272430e`; later documentation commits do not alter it.
- Pixel `pixel-s0-20260914T230335-3649012fd387`; Gaussian `gaussian-s0-20260914T230335-40a3cf2cc7af`; Sparse `sparse-s0-20260914T230335-6f99643d9771`.
- Completed queue evidence: controller `/mnt/research/jepa-worldmodel-study-storage/runs/pilot-queue.json`; worker `runs/three-arm-pilot-queue/queue.json`. Do not restart this completed queue or reuse its recorded PIDs. Per-run training manifests say `training_complete`; separate evaluation metrics say `passed`, and queue says `complete`.
- Latest validated result: checkpoint-only diagnostics on124 held-out episodes show accurate one-step Pixel images but block disappearance from H2 under latent feedback. Encoder-trained probes also misread predicted Pixel latents. This is a substantive baseline/interface confound: the completed pilot does not cleanly isolate pixel versus JEPA objectives. Earlier `passed` denotes execution checks, not validated scientific fairness. Original results remain preserved in [THREE_ARM_PILOT_REPORT.md](THREE_ARM_PILOT_REPORT.md).
- Exact next action: review [PIXEL_FAILURE_ANALYSIS.md](PIXEL_FAILURE_ANALYSIS.md) with the user. Checkpoint-only diagnostics are complete; do not retrain. Proposed decode→re-encode feedback/readout controls are recommendations awaiting authorization, not queued work.
- Pending/unknown: multi-seed generalization, broader simulator initial-state coverage, full-run average GPU utilization, and any future follow-up protocol. No remaining execution/retention blocker for this pilot. Billing-interrupted attempts and upstream reproductions remain preserved.

## Queue and resume details

The completed controller observer is `jepa-pilot-monitor.service`; the detached worker launcher was `study.concurrent_pilot`. Historical reproduction state is `runs/reproduction-queue.json` under durable storage. There is no active run to resume. On continuation, inspect live state before taking action; do not relaunch a completed queue.

Authoritative retained evidence under `/mnt/research/jepa-worldmodel-study-storage/runs/`: `pilot-summary.json`, `pilot-checkpoint-retention.json`, and `pilot-evaluation-artifact-inventory.json`. The report links results and executed commands. Final checkpoints are under the storage root’s `checkpoints/<run_id>/`.

## Completed diagnostic evidence

Inference-only SHA `957c421d7816893f7e935b74e1263c3e9be76cbe`, using the unchanged final Pixel checkpoint; existing Gaussian/Sparse physical metrics reused. No model/probe training. Artifact root `/mnt/research/jepa-worldmodel-study-storage/artifacts/pixel-diagnostics-20260915/` contains visual panels, all evaluated images, metrics, image-summary.json, physical-error PNG/PDF and artifact-inventory.json. Diagnostic inference completed in35.83s; GPU subsequently observed idle. All124 H1 rollout/teacher-forced MSE controls agree within1e-7. Image centroid/axis calculations passed translation/rotation checks; segmentation remains heuristic with invalid detections explicitly reported.

Main limits: D(E) is an untrained composition, not a pure decoder-capacity test; no causal proof of multimodal blur or capacity waste; H32 has only4 episodes. New diagnostic use of test episodes is post-hoc and must not be represented as fresh confirmation for future changes. See the report and newest research-handoff entry for interpretation and proposed next decision.
