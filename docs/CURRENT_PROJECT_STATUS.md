# Current project status

## Completed reproduction goal — 2026-09-14 17:15 UTC

**Gaussian and sparse official PushT reproductions, controller checkpoint retention and final report are complete.**

- Immutable experiment SHA: `0f1720a0be0c73a98a16ce48936c052d7aaee3a6`; upstream `bdd812d9432cccda8c350086006401b436f91982`. Both training seed0; official planning seed99,50 episodes.
- Gaussian: success36/50 (72%); training4h33m18s; planning24m45s; peak training28.864GiB, planning5.754GiB; mean sampled training GPU64.17%.
- Sparse: success40/50 (80%); training3h51m03s; planning24m32s; peak training28.866GiB, planning5.754GiB; mean sampled training GPU76.26%.
- Both463,190,601-byte checkpoints retained on controller and SHA256 independently reverified. Compact manifests, resolved configs, logs, metrics and telemetry retained.
- Full report with exact commands: `docs/UPSTREAM_REPRODUCTION_REPORT.md`; durable original and machine-readable results: `/mnt/research/jepa-worldmodel-study-storage/runs/UPSTREAM_REPRODUCTION_REPORT.md` and `UPSTREAM_REPRODUCTION_RESULTS.json`.
- Systemd `jepa-reproduction-queue.service` exited successfully; queue stage/status both complete. No further jobs scheduled; GPU worker not shut down. Worker disk15G used/36G free, root53M used.
- Initial monitor SSH timeout was repaired without repeating Gaussian; sparse advanced automatically. Supervisor has no tmux dependency. Recoverable infrastructure failures are repaired/retried; no scientific failures are skipped.
- Future checks do not repeatedly update this handoff. If remaining goal ETA is under5 minutes, stay to verify completion and report.
- Reproduction execution gate passed: both models train, plan and produce valid artifacts. Single training seed and50 evaluation episodes do not establish a general advantage or exact paper replication; published target for this cell is not established. Environment compatibility deviations are documented in the report.
- Next scientific work: finish common physical evaluator adapters/splits and validate fair pixel planning before a separately authorized pilot. No pixel research run or larger sweep launched.

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
Pixel baseline is implemented independently, tested for plumbing, and not launched as a research experiment. Common physical metrics/ranking and frozen probes exist; checkpoint/simulator adapters and frozen episode partitions remain unfinished. Both upstream reproduction executions and final metrics are validated above; the controlled three-method comparison remains pending.

Official CEM uses simulator-informed early stopping and couples goal/rollout/prefix; those semantics remain only for reproduction. Upstream checkpoint resume omits/reinitializes parts of state, so exact resumption is not established. Numeric agreement with paper cannot be claimed without an authoritative target for the selected cell. We are testing WHETHER and WHEN JEPA helps, not assuming it wins.

Exact next action: review the completed reproduction report and prepare the common-evaluation pilot; this reproduction queue has no remaining work.

## Live reproduction monitor

Updated automatically from the controller monitor; no scientific result is inferred from an active run.

```json
{
  "source_sha": "0f1720a0be0c73a98a16ce48936c052d7aaee3a6",
  "alias": "autodl-jepa",
  "gaussian_run": "gaussian-s0-20260913T214253-97d19b52dc9f",
  "status": "complete",
  "active_run": "sparse-s0-20260914T125613-d870e47ee0cf",
  "stage": "complete",
  "updated_at": 1789406118.455277,
  "sparse_run": "sparse-s0-20260914T125613-d870e47ee0cf",
  "report": "/mnt/research/jepa-worldmodel-study-storage/runs/UPSTREAM_REPRODUCTION_REPORT.md"
}
```
