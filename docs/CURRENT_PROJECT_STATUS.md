# Current project status

## Current execution
**Full Gaussian upstream reproduction is RUNNING; full reproduction metrics are not available yet.**

- Worker: `autodl-jepa`, RTX5090, driver595.71.05, CUDA runtime12.8.
- Immutable training/evaluation code SHA: `0f1720a0be0c73a98a16ce48936c052d7aaee3a6`.
- Active full Gaussian run: `gaussian-s0-20260913T214253-97d19b52dc9f`.
- Training: official2 epochs, batch64, all1,981,721 windows/epoch,61,930 total optimizer steps. Observed early throughput~3.7–4 steps/s; estimated4–5 training hours per method, excluding planning. Observed GPU use16,794MiB (~16.4GiB),77–81% utilization; final peak/averages pending.
- Controller monitor: tmux session `jepa-reproduction-monitor`; state `/mnt/research/jepa-worldmodel-study-storage/runs/reproduction-queue.json`.
- Sequence enforced: Gaussian training -> official Gaussian planning -> verified checkpoint retention -> sparse training -> official sparse planning -> verified retention -> generated report. Stops on failures. No pixel training or large sweep.
- Compact results sync back every monitoring cycle. Completed report will be `/mnt/research/jepa-worldmodel-study-storage/runs/UPSTREAM_REPRODUCTION_REPORT.md`; it does not exist until both evaluations complete.

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
Pixel baseline is implemented independently, tested for plumbing, and not launched as a research experiment. Common physical metrics/ranking and frozen probes exist; checkpoint/simulator adapters and frozen episode partitions remain unfinished. Full Gaussian/sparse reproduction success, end-to-end planning runtime, final VRAM and checkpoint results are pending.

Official CEM uses simulator-informed early stopping and couples goal/rollout/prefix; those semantics remain only for reproduction. Upstream checkpoint resume omits/reinitializes parts of state, so exact resumption is not established. Numeric agreement with paper cannot be claimed without an authoritative target for the selected cell. We are testing WHETHER and WHEN JEPA helps, not assuming it wins.

Exact next action: continue active Gaussian run; upon successful completion run its official50-episode planning evaluation, then sparse under identical conditions.

## Live reproduction monitor

Updated automatically from the controller monitor; no scientific result is inferred from an active run.

```json
{
  "source_sha": "0f1720a0be0c73a98a16ce48936c052d7aaee3a6",
  "alias": "autodl-jepa",
  "gaussian_run": "gaussian-s0-20260913T214253-97d19b52dc9f",
  "status": "running",
  "active_run": "gaussian-s0-20260913T214253-97d19b52dc9f",
  "stage": "training",
  "updated_at": 1789336238.851039
}
```
