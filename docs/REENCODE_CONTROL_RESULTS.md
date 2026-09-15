# Decode→re-encode control results

Status: **complete**. No training. Planning results are final only when all three conditions have50 episodes and state is complete. Teacher forcing uses privileged simulator prefixes, not deployable model-only planning.

## Physical errors versus horizon

Pusher RMSE / block RMSE / wrapped angle MAE; positions in environment units, angles radians. Same held-out cohorts and frozen linear probe.

| H | N | Original | Decode→re-encode | Teacher-forced oracle |
|---|---:|---|---|---|
|1|124|213.02/169.83/1.57|95.10/39.02/0.44|95.10/39.02/0.44|
|2|124|207.03/143.98/1.57|99.29/41.82/0.45|98.69/42.27/0.46|
|4|124|178.49/131.38/1.27|90.81/49.44/0.57|85.93/44.73/0.53|
|8|124|163.88/118.54/1.02|90.12/61.11/0.61|80.93/41.75/0.44|
|16|106|168.39/94.92/0.62|101.96/76.67/0.70|70.82/34.69/0.40|
|32|4|179.63/41.34/0.30|89.64/88.98/0.77|20.40/19.07/0.24|

## Planning and candidate ranking

| Mode | Finished episodes /50 | Final success | Ever success | Mean regret | Mean Spearman |
|---|---:|---:|---:|---:|---:|
|original|50|0|15|0.00876|-0.076|
|reencode|50|1|28|0.00410|0.173|
|teacher_forced_oracle|50|2|22|0.00347|0.454|

## Interpretation limits

H1 repair is a readout change: no predicted latent has yet been fed back. Longer-horizon differences combine readout and feedback changes. Decode/reencode reduces block error at H1–16 but increases it at H32 in this cohort (only4 episodes); do not claim a complete repair or generalized superiority. Teacher forcing supplies fresh true history at every requested endpoint, so it diagnoses accumulation but is not a feasible open-loop substitute. Interpret planning comparisons only when every condition has50 episodes; partial rows are not final results. The original physical metrics were checked against retained pilot outputs. See docs/REENCODE_CONTROL_PROTOCOL.md for settings, hashes and preserved startup failures.

## Final interpretation

All150 planning episodes completed and were retained. Decode/reencode reduces mean candidate regret by53.2% and improves Spearman from−0.076 to+0.173. Ever-goal attainment improves15/50→28/50 (+26 percentage points), but final success only0/50→1/50 (+2 points). This repairs part of the readout/feedback problem, not the planner as a whole. Block-position error reductions at H1/H2/H4/H8/H16 are77.0%/71.0%/62.4%/48.4%/19.2%; H32 worsens (only4 episodes). No cross-horizon monotonicity claim is justified because cohorts/target states differ.

The teacher-forced oracle yields regret0.00347 and Spearman0.454, yet only2/50 final successes and22/50 ever successes. Privileged true prefixes improve ranking but do not produce robust closed-loop goal achievement. Removing long-rollout accumulation alone is therefore insufficient in this fixed-probe/fixed-planner setup. Residual probe geometry, goal retention and planning-horizon/cost limitations remain candidate explanations, not causally isolated findings. The oracle is not ground-truth-cost planning: its final prediction and readout still use the learned model and frozen probe. It is also not a deployable model-only planner or a fair compute baseline.

These remain one-seed, post-hoc diagnostics on the same test episodes/banks. Final success counts are small; do not treat the numerical differences as proof of generalized performance improvement. No training was performed, and none is authorized by completion of this control. Next step is user review of the residual bottlenecks and a separately authorized diagnostic or training design.

## Runtime, provenance and retained evidence

Original planning/ranking stage349.68s (5m50s); reencode748.48s (12m28s); oracle21128.88s (5h52m09s). The oracle simulates candidate prefixes and its wall time includes that privileged computation. Active execution SHA `23083327db0c21eb1a4787e032313c7691778d06`; reused horizon inference SHA `1e7fbc592d1b44be09cba7a5cc00f83acc0bf3b7`; unchanged checkpoint training SHA `40d8c7840a0a7e96933a42e10c60a926b272430e`. See [REENCODE_CONTROL_PROTOCOL.md](REENCODE_CONTROL_PROTOCOL.md) for exact configuration and preserved startup failures.

Artifacts: `/mnt/research/jepa-worldmodel-study-storage/artifacts/reencode-control-20260915-r3/`: state.json, open-loop.json, three banks.json files,150 per-bank score NPZ files, summary.json and retention-verification.json. Worker/controller hashes verified for all155 raw JSON/NPZ outputs. Each condition has50 identical seed/bank hashes and10 replans per episode. Original open-loop metrics and candidate scores reproduced retained pilot values; checkpoint hash unchanged at completion. No test-set fitting or new probe was used.

Queue completed 2026-09-15 18:55:04 UTC.
