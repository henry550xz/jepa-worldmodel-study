# Upstream PushT reproduction results

Generated from completed run manifests and upstream final evaluation logs. These are official-protocol reproductions, not the controlled three-arm study.

| Method | Run | Train wall s | Planning wall s | Train peak VRAM GiB | Planning peak VRAM GiB | Mean sampled GPU % | Checkpoint MiB | Success rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| gaussian | gaussian-s0-20260913T214253-97d19b52dc9f | 16397.993 | 1484.618 | 28.864 | 5.754 | 64.170 | 441.733 | 0.720 |
| sparse | sparse-s0-20260914T125613-d870e47ee0cf | 13863.054 | 1472.085 | 28.866 | 5.754 | 76.257 | 441.733 | 0.800 |

## Exact provenance and commands

- gaussian: code `0f1720a0be0c73a98a16ce48936c052d7aaee3a6`, upstream `bdd812d9432cccda8c350086006401b436f91982`, dataset SHA256 `442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08`.
- Environment: Python 3.12.3, PyTorch 2.8.0+cu128, CUDA runtime 12.8; GPU NVIDIA GeForce RTX 5090.
```bash
cd /root/autodl-tmp/robotics/jepa-worldmodel-study/code/0f1720a0be0c73a98a16ce48936c052d7aaee3a6
/root/autodl-tmp/robotics/jepa-worldmodel-study/envs/lpwm-5090/bin/python -m study.run --method gaussian --phase reproduction --seed 0 --dataset-version 442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08
/root/autodl-tmp/robotics/jepa-worldmodel-study/envs/lpwm-5090/bin/python -m study.plan_official gaussian-s0-20260913T214253-97d19b52dc9f
```
Resolved training and planning configs, logs and metrics are under `runs/gaussian-s0-20260913T214253-97d19b52dc9f`; selected checkpoint plus verified SHA256 under `checkpoints/gaussian-s0-20260913T214253-97d19b52dc9f`.

- sparse: code `0f1720a0be0c73a98a16ce48936c052d7aaee3a6`, upstream `bdd812d9432cccda8c350086006401b436f91982`, dataset SHA256 `442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08`.
- Environment: Python 3.12.3, PyTorch 2.8.0+cu128, CUDA runtime 12.8; GPU NVIDIA GeForce RTX 5090.
```bash
cd /root/autodl-tmp/robotics/jepa-worldmodel-study/code/0f1720a0be0c73a98a16ce48936c052d7aaee3a6
/root/autodl-tmp/robotics/jepa-worldmodel-study/envs/lpwm-5090/bin/python -m study.run --method sparse --phase reproduction --seed 0 --dataset-version 442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08
/root/autodl-tmp/robotics/jepa-worldmodel-study/envs/lpwm-5090/bin/python -m study.plan_official sparse-s0-20260914T125613-d870e47ee0cf
```
Resolved training and planning configs, logs and metrics are under `runs/sparse-s0-20260914T125613-d870e47ee0cf`; selected checkpoint plus verified SHA256 under `checkpoints/sparse-s0-20260914T125613-d870e47ee0cf`.

## Deviations and interpretation

The RTX5090 environment preserves working torch2.8/cu128 rather than upstream2.3/cu121; Python3.12, Hydra1.3.2, W&B.17.9, scikit-image.24 and NumPy1.26.4 are disclosed compatibility choices. See the committed environment inventory and requirements. Upstream scientific source is unchanged; logging/output locations and instrumentation differ.
Training and planning wall times include their diagnostics and startup; model-only latency is not separately instrumented. Sampled GPU utilization is not continuous measurement. Official CEM permits simulator-based early stopping and couples goal horizon, rollout horizon and action prefix. State distance mixes units; use the future common physical evaluator for controlled comparisons.
Completing these runs validates executable behavior, not numerical agreement with a published target: no authoritative expected success rate for this exact selected cell has been established in the repository audit. Inspect curves and planning outcomes before deciding whether the baseline is scientifically reproduced closely enough. No pixel experiment or multi-seed sweep is authorized by this queue.

## Final worker disk usage

```text
Filesystem     Type     Size  Used Avail Use% Mounted on
overlay        overlay   30G   53M   30G   1% /
/dev/md0       xfs       50G   15G   36G  30% /root/autodl-tmp
```
