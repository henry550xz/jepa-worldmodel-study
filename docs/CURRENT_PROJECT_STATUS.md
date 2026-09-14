# Current project status

## Current execution
**Gaussian training and official planning completed successfully. The controller monitor FAILED during the planning launch; the sequential queue is halted before checkpoint retention and sparse reproduction.**

- Worker: `autodl-jepa`, RTX5090, driver595.71.05, CUDA runtime12.8.
- Immutable training/evaluation code SHA: `0f1720a0be0c73a98a16ce48936c052d7aaee3a6`.
- Completed full Gaussian run: `gaussian-s0-20260913T214253-97d19b52dc9f`.
- Training: official2 epochs, batch64, all1,981,721 windows/epoch,61,930 total optimizer steps. Latest measured progress and ETA are recorded below; final peak VRAM and full-run utilization averages remain pending.
- Controller monitor: tmux session `jepa-reproduction-monitor`; state `/mnt/research/jepa-worldmodel-study-storage/runs/reproduction-queue.json`.
- Sequence enforced: Gaussian training -> official Gaussian planning -> verified checkpoint retention -> sparse training -> official sparse planning -> verified retention -> generated report. Stops on failures. No pixel training or large sweep.
- Compact results sync back every monitoring cycle. Completed report will be `/mnt/research/jepa-worldmodel-study-storage/runs/UPSTREAM_REPRODUCTION_REPORT.md`; it does not exist until both evaluations complete.

## Latest operator check — 2026-09-14 12:46 UTC

- No active JEPA job. Controller tmux monitor is absent; queue records `watcher_failed` / `TimeoutExpired`. Its `stage=training` is stale and does not reflect completed worker evaluation.
- Gaussian run `gaussian-s0-20260913T214253-97d19b52dc9f`: training exit0, completed02:16:14 UTC; official50-episode planning exit0, completed02:42:00 UTC. Final success rate0.72 (36/50); upstream mean_state_dist197.0362. These results establish successful execution, not paper-level numerical agreement.
- Measured training wall time16,397.99s (4h33m18s),61,930 steps; whole-run effective throughput3.777 steps/s. Training peak allocated VRAM30,992,848,384 bytes (~28.86GiB). Planning wrapper wall time1,484.62s (24m45s), instrumented process1,475.55s; peak allocated6,178,473,472 bytes (~5.75GiB).
- Worker GPU idle:0% utilization,2MiB used; no Python processes listed. Worker data disk37G free, root30G free/53M used. Gaussian latest checkpoint exists,463,190,601 bytes. Compact manifests/logs/configs/metrics retrieved to controller project storage; selected checkpoint hash-verified retention remains pending. Preserve worker storage.
- Failure diagnosis: controller SSH launch timed out after45s at approximately02:17:58 UTC. The command backgrounds the entire `cd ... && nohup ...` list; the background shell can retain SSH output descriptors despite the inner command redirections. This is the likely launch timeout cause. Worker planning nevertheless ran to successful completion. No failed scientific stage is indicated; orchestration failed and did not recover.
- Only sparse smoke exists; full sparse reproduction has not launched. No duplicate jobs, retries, pixel experiments or scientific queue advancement performed during this check. Logs/artifacts preserved.
- ETA: no running-stage ETA while queue is halted. Gaussian training/planning remaining0. After recovery, sparse training is estimated4h33m from measured Gaussian full-run time; sparse planning remains unmeasured (Gaussian's24m45s is only a reference). Total completion time remains unknown until recovery and sparse execution.
- Next action: correct persistent launch detachment in the controller watcher, verify resume logic against completed Gaussian manifests, then explicitly resume the existing queue without rerunning Gaussian. Resume should retain/hash-check Gaussian checkpoint before launching sparse. Per operator failure workflow, this session diagnoses, records, reports and exits; no automatic next stage is currently possible.

## Git / completed setup
Canonical checkout `/mnt/research/robotics/jepa-worldmodel-study` on mounted research disk; durable artifacts in sibling project storage. Initial upstream/main and local main match `bdd812d9432cccda8c350086006401b436f91982`, annotated tag `baseline/upstream-initial`.

Current development branch `study/pixel-baseline`; current documentation/monitor HEAD is obtained with `git rev-parse HEAD` (it can be newer than immutable experiment SHA). Common foundation preserved on `study/common-eval` through01f2126. Small logical commits cover scaffold, source audit, common evaluator, deployment, pixel design/implementation and tests. Upstream scientific source files are unchanged.

Origin fetch: git@github.com:henry550xz/jepa-worldmodel-study.git; origin push: https://github.com/henry550xz/jepa-worldmodel-study.git using repo-local gh credential helper. Upstream: https://github.com/YilunKuang/lpworldmodel.git. Existing SSH deploy key lacks fork push permission; HTTPS push succeeded without changing SSH configuration. Initial branches/tag backed up to GitHub; latest documentation commits are pushed periodically.

## Validated environment and data
Dedicated data-disk venv `envs/lpwm-5090` inherits base torch2.8.0+cu128 and torchvision.23.0+cu128 read-only, Python3.12.3. No base packages, drivers, system CUDA or bash startup files changed. Environment664M; root overlay remained53M used; worker data disk had38G available after setup/smokes and full-run start.

Targeted compatibility changes from upstream Python3.9/torch2.3: Hydra1.3.2, W&B.17.9, scikit-image.24, local NumPy1.26.4 override. Effective inventory: manifests/WORKER_ENVIRONMENT_5090.json; exact requirements/constraints in conf/study. Trusted official data/self-generated checkpoints use TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 for the newer PyTorch loading default. No unrelated old transformers/tokenizers packages installed.

Tsinghua/Aliyun/PyPI/OSF/PyTorch connectivity tested before downloads. Official PushT archive SHA256 `442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08` verified. Acquisition/extraction304.881s; compressed2,785,304,515 bytes, uncompressed7,370,447,305. Worker path datasets/pusht_noise. Train18,685 episodes /2,336,736 raw frames; validation21 episodes /2,514 frames. Batch tensors match code map.

## Completed gates
- pip check; train.py/plan.py imports; PushT reset; CUDA SDPA forward/backward: passed.
- Controller lightweight tests:10 passed, Torch skipped. Worker correctness tests:21 passed, including pixel loss gradients/causality/action influence/tiny overfit. These are synthetic plumbing checks, not research results.
- Gaussian dataset smoke `gaussian-s0-20260913T214005-c6af006c0be4`: complete,10.424s process wall,1,828,423,680 peak allocated VRAM bytes.
- Sparse dataset smoke `sparse-s0-20260913T214117-05d8b6b356e8`: complete,10.354s,1,829,343,744 peak bytes.
- Both smoke latest checkpoints463,359,923 bytes; compact manifests/logs retained on controller.
- Earlier Gaussian smoke failed before model construction due imported Hydra config-path resolution. Fixed in wrapper with absolute config path; failed manifest retained. No upstream model/config change.

## Scientific readiness / blockers
Pixel baseline is implemented independently, tested for plumbing, and not launched as a research experiment. Common physical metrics/ranking and frozen probes exist; checkpoint/simulator adapters and frozen episode partitions remain unfinished. Gaussian execution and metrics are validated above; sparse full reproduction and the final comparison remain pending.

Official CEM uses simulator-informed early stopping and couples goal/rollout/prefix; those semantics remain only for reproduction. Upstream checkpoint resume omits/reinitializes parts of state, so exact resumption is not established. Numeric agreement with paper cannot be claimed without an authoritative target for the selected cell. We are testing WHETHER and WHEN JEPA helps, not assuming it wins.

Exact next action: repair controller monitor launch detachment and resume the existing queue after checking completed Gaussian evidence; retain its checkpoint, then run sparse under identical conditions.

## Live reproduction monitor

Updated automatically from the controller monitor; no scientific result is inferred from an active run.

```json
{
  "source_sha": "0f1720a0be0c73a98a16ce48936c052d7aaee3a6",
  "alias": "autodl-jepa",
  "gaussian_run": "gaussian-s0-20260913T214253-97d19b52dc9f",
  "status": "watcher_failed",
  "active_run": "gaussian-s0-20260913T214253-97d19b52dc9f",
  "stage": "training",
  "updated_at": 1789352278.4697206,
  "error_type": "TimeoutExpired",
  "error": "Command '['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'UpdateHostKeys=no', '-o', 'ConnectTimeout=20', '-o', 'ServerAliveInterval=30', '-o', 'ServerAliveCountMax=4', 'autodl-jepa', 'cd /root/autodl-tmp/robotics/jepa-worldmodel-study/code/0f1720a0be0c73a98a16ce48936c052d7aaee3a6 && nohup /root/autodl-tmp/robotics/jepa-worldmodel-study/envs/lpwm-5090/bin/python -m study.plan_official gaussian-s0-20260913T214253-97d19b52dc9f > /root/autodl-tmp/robotics/jepa-worldmodel-study/runs/gaussian-s0-20260913T214253-97d19b52dc9f/planning-launch.log 2>&1 < /dev/null &']' timed out after 45 seconds"
}
```
