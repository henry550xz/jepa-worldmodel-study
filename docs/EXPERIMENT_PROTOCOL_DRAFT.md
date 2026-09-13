# Controlled world-model study: draft protocol

We are testing WHETHER and WHEN JEPA helps. We are not assuming JEPA must win.

## Arms and stages
Observation/pixel prediction versus Gaussian JEPA (dense LeWM) versus sparse JEPA (LpWM). Start with PushT. OGBench Cube and controlled synthetic dynamics follow only after a validated pilot; PDEBench is optional. No MARL, old LeRobot, Koopman or LEON integration.

First reproduce official dense/sparse settings unchanged. Separately run a three-arm seed-0 pilot to measure feasibility, not statistical superiority. Do not start a five-seed sweep before runtime, peak memory, checkpoint size and planning cost are known.

## Controlled training
Share raw trajectories, preprocessing, observation history (3), action grouping (5 simulator actions/model step), ViT encoder and AdaLN predictor dimensions. Use the same split, seeds, minibatch order, update budget and checkpoint-selection rule. Preserve official muP initialization/optimizer settings for reproduction. Pixel decoder adds capacity and compute: report both parameter counts and wall-time/FLOP estimates; equal updates is not equal compute. Do not tune on final evaluation episodes. Separate reproduction from any study-specific changes.

## Data separation and probes
Upstream loads distinct train/ and val/ directories; split_ratio is not applied. Before study training, freeze episode-ID partitions for world-model train/validation, probe train/validation/test and final planning evaluation. Never split overlapping windows randomly across partitions. If data are insufficient, explicitly label in-distribution probes trained on world-model-training episodes and keep held-out probe/test episodes disjoint. Record hashes and episode IDs; no fabricated split sizes.

Freeze encoder weights and use eval mode. Fit linear and small one-hidden-layer MLP probes using only probe-training data, selecting regularization/epochs on probe validation. Fit feature/target normalization only on probe train. Predict pusher x/y, block x/y, sin(angle), cos(angle), and optionally pusher vx/vy. Velocity from a single image may be unidentifiable; report history-based velocity probes separately.

## Common physical evaluation
Report position RMSE in simulator coordinates, circular angular MAE in radians, and velocity error separately. Do not aggregate incompatible units without a preregistered scale. Horizons 1,2,4,8,16,32 are MODEL steps (multiply by frameskip=5 for simulator actions); skip unsupported windows with explicit reasons/counts.

For each horizon evaluate (a) probe(true future encoding) against true physical state and (b) the SAME probe(predicted future encoding) against that state. Report paired errors, not latent MSE across methods. Their difference is a diagnostic, not an exact additive decomposition of error.

## Candidate ranking
Freeze initial simulator states, seeds, goals and candidate action tensors on disk with hashes. Every method receives identical candidates and action normalization; simulator quality is evaluated once per bank. Use top-1 regret, tie-aware Spearman rank correlation, top-k overlap and best-candidate top-k hit rate. Lower cost is better. A method adapter must define its quality score: latent goal distance versus pixel goal distance is a confound, so add a shared frozen physical-probe cost comparison. Simulator restoration must be validated before interpreting rankings.

## Closed-loop planning
Separate goal_horizon, rollout_horizon, execute_prefix, max_replans and CEM samples/elites/iterations. Record success, final physical error, completion simulator steps, model-only planning latency, total evaluation wall time and actual calls to model/simulator. Compare the same CEM compute budget; disable simulator-based CEM early stopping for controlled study evaluation. Official reproduction retains upstream early stopping and horizon coupling and is labeled accordingly.

## Reproducibility and retention
Only committed snapshots run. Each run records unique ID, method, git SHA, upstream SHA, seed, dataset version/path, resolved configs, GPU model, timestamps, wall time, measured or explicitly unavailable VRAM, checkpoints, planning/evaluation settings and metrics paths. Save compact results frequently; verify selected checkpoint hashes before destroying a worker. Upstream checkpoints are NOT proven exact resumable training state (see code map).

## Queue
1. Gaussian tiny plumbing smoke; 2. sparse tiny plumbing smoke.
3. Official Gaussian PushT (training seed 0, evaluation seed 99).
4. Official sparse PushT under identical conditions.
5. Pixel seed-0 pilot after correctness gates; 6. Gaussian seed-0 pilot; 7. sparse seed-0 pilot.
No results exist yet. No worker has been selected or contacted.
