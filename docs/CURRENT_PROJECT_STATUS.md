# Current project status

## Current execution
**Sparse official reproduction is training normally under systemd supervision. Gaussian training/planning and hash-verified controller checkpoint retention are complete.**

- Worker: `autodl-jepa`, RTX5090, driver595.71.05, CUDA runtime12.8.
- Immutable training/evaluation code SHA: `0f1720a0be0c73a98a16ce48936c052d7aaee3a6`.
- Completed full Gaussian run: `gaussian-s0-20260913T214253-97d19b52dc9f`.
- Training: official2 epochs, batch64, all1,981,721 windows/epoch,61,930 total optimizer steps. Latest measured progress and ETA are recorded below; final peak VRAM and full-run utilization averages remain pending.
- Controller supervisor: systemd service `jepa-reproduction-queue.service`; state `/mnt/research/jepa-worldmodel-study-storage/runs/reproduction-queue.json`.
- Sequence enforced: Gaussian training -> official Gaussian planning -> verified checkpoint retention -> sparse training -> official sparse planning -> verified retention -> generated report. Stops on failures. No pixel training or large sweep.
- Compact results sync back every monitoring cycle. Completed report will be `/mnt/research/jepa-worldmodel-study-storage/runs/UPSTREAM_REPRODUCTION_REPORT.md`; it does not exist until both evaluations complete.

## Latest operator check — 2026-09-14 15:23:34 UTC

- Active run: `sparse-s0-20260914T125613-d870e47ee0cf`, official training, immutable source SHA unchanged. Systemd queue active/running, zero restarts; no duplicate jobs launched.
- Epoch2:8,563/30,965; overall39,528/61,930 steps (63.83%). Recent200-step window took44s:4.545 steps/s. Log age0.13s; progress advancing, no traceback/OOM/NaN/Inf/no-space matches in training log.
- GPU: one training compute process; observed92% utilization,31,070/32,607MiB memory (~95.3%). Recent logged samples83% and77%. VRAM is high but no OOM detected. Worker data disk36G free; root30G free/53M used.
- Gaussian retained controller checkpoint SHA256 rechecked against saved worker hash: matches. Completed Gaussian success rate72% (36/50); no rerun.
- Current sparse training ETA: approximately1h22m remaining, **16:46 UTC September14**, extrapolated from recent measured throughput, excluding validation/checkpoint overhead. Gaussian stages remaining0. Sparse official planning duration remains unmeasured; Gaussian24m45s is a reference only. Remaining queue:1h22m training + unknown sparse planning + retention/report overhead.
- Automatic next step: sparse official planning → hash-verified retention → final reproduction report. Healthy service left alone; no pixel jobs. Earlier GPU-CSV inspection used the wrong column and was corrected; that diagnostic exception was local to this check, not an experiment failure.

## Supervisor recovery — 2026-09-14 12:53 UTC

- Repaired the SSH launch timeout: worker Python Popen starts a new session with all standard descriptors redirected and closes inherited descriptors. Worker flock prevents overlapping launches; controller flock prevents duplicate monitors. Local functional regression check verified immediate return and one child for two competing launches.
- Committed supervisor/rule fix `fd4880f`. Scientific worker snapshot remains `0f1720a0be0c73a98a16ce48936c052d7aaee3a6`; Gaussian is not rerun.
- Enabled and started systemd `jepa-reproduction-queue.service`, restart-on-failure with60s delay, mount dependency and boot persistence. Scientific/protocol RuntimeError exits78 prevent blind restarts. No tmux required. Service logs append to existing reproduction-watcher.log; prior failure evidence preserved.
- Rule clarified: repair recoverable infrastructure failures and safely resume within authorization; reporting an error alone does not finish the task. Interactive sessions exit after verifying persistent execution, not after abandoning recoverable errors.
- Service reconciles completed Gaussian manifests, retrieves compact evidence, hash-verifies retained checkpoint, then launches sparse training/planning and generates final report. Live state below is authoritative for current stage. Full study is not yet complete.
- Remaining sparse training estimate ~4h33m based on Gaussian full-run timing; sparse planning unmeasured (Gaussian24m45s reference), plus checkpoint transfer time. Do not claim an exact final completion time before sparse starts.

## Previous failure diagnosis — 2026-09-14 12:46 UTC

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

Exact next action: let active sparse training finish; systemd advances its official planning, checkpoint retention and report. Inspect live state and repair recoverable failures on continue.

## Live reproduction monitor

Updated automatically from the controller monitor; no scientific result is inferred from an active run.

```json
{
  "source_sha": "0f1720a0be0c73a98a16ce48936c052d7aaee3a6",
  "alias": "autodl-jepa",
  "gaussian_run": "gaussian-s0-20260913T214253-97d19b52dc9f",
  "status": "running",
  "active_run": "sparse-s0-20260914T125613-d870e47ee0cf",
  "stage": "training",
  "updated_at": 1789399387.2415724,
  "sparse_run": "sparse-s0-20260914T125613-d870e47ee0cf"
}
```
