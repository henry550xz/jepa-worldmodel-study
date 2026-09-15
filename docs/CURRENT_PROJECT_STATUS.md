# Current project status

Working snapshot; research history is in [CHATGPT_RESEARCH_HANDOFF.md](CHATGPT_RESEARCH_HANDOFF.md). Updated 2026-09-15 for the documentation split; worker observations below retain their actual timestamps. No new worker audit was performed for this edit.

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
- Latest validated result: complete matched pilot with mixed scientific outcomes, documented in [THREE_ARM_PILOT_REPORT.md](THREE_ARM_PILOT_REPORT.md). `passed` describes evaluator completion, not favorable scientific performance.
- Exact next action: review the report with the user; await authorization for any additional experiment or changed protocol. Recommended discussion: weak Pixel predicted-state decoding, negative Sparse candidate ranking, goal retention, and broader simulator coverage. These recommendations do not authorize runs.
- Pending/unknown: multi-seed generalization, broader simulator initial-state coverage, full-run average GPU utilization, and any future follow-up protocol. No remaining execution/retention blocker for this pilot. Billing-interrupted attempts and upstream reproductions remain preserved.

## Queue and resume details

The completed controller observer is `jepa-pilot-monitor.service`; the detached worker launcher was `study.concurrent_pilot`. Historical reproduction state is `runs/reproduction-queue.json` under durable storage. There is no active run to resume. On continuation, inspect live state before taking action; do not relaunch a completed queue.

Authoritative retained evidence under `/mnt/research/jepa-worldmodel-study-storage/runs/`: `pilot-summary.json`, `pilot-checkpoint-retention.json`, and `pilot-evaluation-artifact-inventory.json`. The report links results and executed commands. Final checkpoints are under the storage root’s `checkpoints/<run_id>/`.
