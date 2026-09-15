# Mechanism readiness audit

Four batch32 FP32 seed0 training smokes passed (8 updates +2 validation batches) and14 bounded correctness/theory tests passed. This is plumbing validation, not scientific performance. No full runs launched or authorized.

Training snapshot `1ab94751e93e5f0e73cdab775db3400406323b9f`; shared architecture/init module hashes, parameter counts and first input batch hash are identical across all four arms. Resolved configs and telemetry are retained under each run ID below. Total instantiated parameters40,208,193; Gaussian leaves1,237,843 decoder parameters dormant, so loss-connected parameter counts differ by design.

| Arm | Peak allocated/reserved GiB | Compute-only windows/s | Encoder frames/update | Run ID |
|---|---:|---:|---:|---|
|pixel|11.24/12.46|222.4|160|mechanism-pixel-s0-c504959a2139|
|pixel_rollout|7.77/8.41|296.7|96|mechanism-pixel_rollout-s0-5a5b5132ca75|
|pixel_consistency|12.88/14.08|199.7|192|mechanism-pixel_consistency-s0-fbdedcd0131b|
|gaussian|11.36/11.90|207.7|192|mechanism-gaussian-s0-f38a623b80bf|

Throughput averages updates3–8 and excludes loader waiting, initialization and validation. Six measured updates are not a full-run runtime estimate. No simultaneous-arm VRAM assumption is made;16GiB is tight for the largest arm,24GiB+ is a safer single-arm working budget pending longer profiling. Current5090 is suitable for sequential bounded tests.

Each arm executes288 predictor context tokens and160 action tokens per batch; pixel arms decode96 frames while Gaussian does not decode during training. Encoder frame counts above are derived from the audited source: upstream invokes encoder.forward directly, bypassing the first instrumentation hook. Future instrumentation explicitly counts encode_obs; the retained measurements are not mislabeled as measured encoder calls.

## Information and compute finding

Shared external trajectories, target times, data partition/order, initialization and optimizer schedule are matched. Teacher-forced arms consume true intermediate context; free-running Pixel intentionally does not. No target/later image is supplied to the predictor of that target. Exact conditioning information therefore differs as the mechanism intervention, and this must remain explicit.

Exact compute equality does not hold: objective-specific encoder/decoder/regularizer and backward workloads differ; measured rates vary by about49% between fastest and slowest. Matching FLOPs/wall-time while also matching updates and data exposure is not achieved by these configurations. Proposed primary comparison: matched windows/updates with measured resource reporting; a separately budget-matched comparison would use different update counts and must be declared as such. Do not silently pad with useless compute or claim both are simultaneously matched.

## Remaining gate status

All four common-evaluator smokes passed under SHA `0e7c3f69f68f2d09c36654fa96d3876468092bb4`: each has4 readiness episodes at all6 horizons, the same1 candidate bank,2 bounded replans, physical metrics, frozen-probe fits, action-order/prefix checks and4×6 temporal closure records. Pixel arms also have cycle closure. Evaluation-stage times13.06/12.88/12.57/10.88s (Pixel/rollout/consistency/Gaussian), excluding the separately appended closure pass. No smoke metric is a research result. Strict equal-compute readiness is not claimed. The proposed(beta,rho) theory is still undefined in available project material; [LINEAR_GAUSSIAN_PROVISIONAL.md](LINEAR_GAUSSIAN_PROVISIONAL.md) documents the separately labeled candidate simulation and its25 CPU-only cells,43/43 away-from-boundary matches and3 tests. The user must supply the intended definitions before correspondence can be established.


## Gate disposition

**BOUNDED_TRAINING_AND_EVALUATION_GATES_PASSED. FULL_RUN_GATE_CLOSED.** No active GPU job remains. Resolve the information/compute interpretation before freezing full-run budgets; fixed windows/updates is the recommended primary comparison, with objective-specific compute explicitly measured rather than claimed equal. The auxiliary coefficient1.0 and training horizon3 remain draft choices. The exact requested theory correspondence is blocked until beta/rho and the intended analytic boundary are supplied.

Training configs/telemetry come from SHA `1ab94751e93e5f0e73cdab775db3400406323b9f`. Later runner wiring reads the same settings from the checked-in JSON, adds explicit encoder workload accounting and retains bounded update caps; tested numerical configuration values are unchanged. Do not mistake later orchestration/documentation commits for a new trained checkpoint. Initial80-update tiny-test failure and first evaluator-prefix failure remain preserved; no scientific loss weight or test tolerance was tuned to pass.
