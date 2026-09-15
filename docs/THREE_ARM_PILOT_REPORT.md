# Three-arm seed-0 pilot results

Training and common evaluations completed September 15, 2026 at 10:38:58 UTC (06:38:58 EDT). This is one seed, two training epochs, not a final multi-seed study. We are testing WHETHER and WHEN JEPA helps.

## Provenance and validation

Immutable training/evaluator SHA `40d8c7840a0a7e96933a42e10c60a926b272430e`; upstream `bdd812d9432cccda8c350086006401b436f91982`. Frozen `conf/study/pilot.json` and `manifests/PUSHT_PARTITIONS.json` unchanged. Each arm completed 115,308 updates, batch32 FP32; RTX5090, isolated Python3.12.3/PyTorch2.8.0+cu128. All evaluator statuses passed, with identical partition selection/hash, 50 candidate-bank hashes/seeds and planning settings across methods. Each evaluated 124 held-out episodes for open-loop metrics and 50 simulator banks with10 replans each. Training logs reached epoch2 step57,654 with no detected traceback/OOM/nonfinite loss.

Raw manifests, resolved configs, logs, metrics and aggregate `pilot-summary.json` are under `/mnt/research/jepa-worldmodel-study-storage/runs/`. Final checkpoint retention records are in `pilot-checkpoint-retention.json` there. Original billing-interrupted attempts remain preserved; completed retries restarted from seed0 and did not resume optimizer state.

## Runtime and resources

| Arm | Training wall | Common evaluation wall | Peak allocated/reserved GiB | Final checkpoint MB |
|---|---:|---:|---:|---:|
|pixel|10h30m01s|0h20m55s|7.70/8.89|478.1|
|gaussian|10h41m11s|0h16m09s|7.81/8.13|463.2|
|sparse|10h29m49s|0h16m49s|7.81/8.13|463.2|

Training ran concurrently; evaluations sequentially. Whole successful queue took about11h35m, excluding the lost billing-interrupted attempt and later retention. Evaluation wall times include probe fitting, open-loop evaluation, candidate-bank work and CEM; they are not planning-only times. GPU is now idle; worker data disk27GB free at verification. Full-run average GPU utilization was not collected by the queue; earlier spot checks are not a full-run average. Benchmark measurements remain in CONCURRENCY_BENCHMARK.md.

## Closed-loop physical-goal and candidate ranking

These are synthetic reachable goals from a fixed simulator initial configuration and sampled actions, NOT the official PushT target-coverage benchmark. Success requires the norm of the four position errors below20 and wrapped angle error below pi/9. Report final-step success separately from ever attaining the threshold: all10 replans execute without early stopping. These counts must not be compared directly with upstream36/50 and40/50.

| Arm | Final success /50 | Ever success /50 | Mean final physical cost | Mean ranking Spearman | Mean top1 regret | Mean CEM seconds/replan |
|---|---:|---:|---:|---:|---:|---:|
|pixel|0|15|0.05742|-0.076|0.00876|1.528|
|gaussian|6|30|0.00617|0.271|0.00415|1.505|
|sparse|1|14|0.01391|-0.115|0.01030|1.572|

Gaussian performs best on these ranking and final physical-goal metrics. Sparse and Pixel have negative average ranking correlations in this pilot; this is a negative result to preserve, not grounds to alter the test or rerun until favorable. Low final success and loss of earlier goal attainment warrant investigation before expanding scope. No additional experiment is authorized.

## Frozen representation probes

Held-out test metrics; position RMSE in environment coordinates, angle MAE radians. Probe train/validation/test episodes are separate. Both probes fit500 steps; MLP width64. Planning and open-loop evaluations use the linear probe, not a method-specific selection of whichever probe scores best.

| Arm / probe | Pusher RMSE | Block RMSE | Angle MAE |
|---|---:|---:|---:|
|pixel / linear|88.14|36.75|0.364|
|pixel / mlp|75.24|19.96|0.149|
|gaussian / linear|30.56|29.96|0.697|
|gaussian / mlp|21.92|25.44|0.436|
|sparse / linear|26.22|27.03|0.530|
|sparse / mlp|15.41|19.30|0.248|

Sparse has the best position probe errors; Pixel has the best angle probe error. Thus probe quality alone does not predict the candidate-ranking result.

## Physical error versus horizon

Linear-probe block-position RMSE, aggregated by square root of mean per-episode squared RMSE. Each eligible episode contributes one target at each horizon; sample count varies with available sequence length. R/P denotes true-future representation / predicted-future representation. Difference is diagnostic, not an additive decomposition of independent error sources. Full pusher/block/angle aggregates are retained in `pilot-summary.json`.

| Horizon | Episodes | Pixel R/P | Gaussian R/P | Sparse R/P |
|---|---:|---:|---:|---:|
|1|124|39.54/169.83|39.60/39.42|35.24/40.28|
|2|124|40.58/143.98|39.20/39.27|34.25/40.03|
|4|124|46.02/131.38|36.98/37.78|32.08/38.38|
|8|124|42.55/118.54|30.81/35.93|29.42/38.20|
|16|106|35.18/94.92|21.61/47.83|20.53/54.78|
|32|4|22.18/41.34|6.86/24.98|8.36/52.54|

## Executed commands and run identities

Worker working directory: `/root/autodl-tmp/robotics/jepa-worldmodel-study/code/40d8c7840a0a7e96933a42e10c60a926b272430e`. Isolated interpreter: `/root/autodl-tmp/robotics/jepa-worldmodel-study/envs/lpwm-5090/bin/python`. Persistent launcher: `python -u -m study.concurrent_pilot --authorized-full-pilot`, with GPU0 selected. Commands below document the completed run, not an instruction to launch again:

```bash
python -m study.run --method pixel --phase pilot --seed 0 --dataset-version 442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08
python -m study.run --method gaussian --phase pilot --seed 0 --dataset-version 442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08
python -m study.run --method sparse --phase pilot --seed 0 --dataset-version 442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08
# After all three training processes succeeded, sequentially:
python -m study.evaluate_common pixel-s0-20260914T230335-3649012fd387 --profile pilot
python -m study.evaluate_common gaussian-s0-20260914T230335-40a3cf2cc7af --profile pilot
python -m study.evaluate_common sparse-s0-20260914T230335-6f99643d9771 --profile pilot
```

Dataset remains worker `datasets/pusht_noise`; runtime data/environment/caches/checkpoints stayed under the project data disk. Candidate artifacts and probe weights are retained alongside metrics, with an inventory in `runs/pilot-evaluation-artifact-inventory.json`. All50 candidate-bank hashes match the recorded hashes for every arm. Final checkpoint SHA256 records separately verify controller copies against worker originals.

## Limits and next decision

This pilot establishes an executable matched comparison, not universal JEPA superiority. One seed, short training, fixed initial simulator setup, limited CEM horizon/budget, representation-probe error and decoder parameter/compute differences constrain interpretation. `passed` means evaluator checks completed, not scientific success or favorable model performance. Recommended next action is review these results and approve a specific follow-up protocol if desired; do not start another sweep automatically.

Only four held-out episodes support horizon32; that horizon is especially underpowered. Counts at different horizons differ, so decreasing aggregate error with horizon is not evidence that long rollouts improve. The pixel predicted-state error is much larger than true-observation probe error; investigate this representation/dynamics interface before a larger study, without retroactively changing the completed protocol.
