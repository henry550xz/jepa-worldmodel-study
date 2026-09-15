# Frozen Pixel decode→re-encode control

Authorized by the user on 2026-09-15. No model or probe training; reuse the final Pixel checkpoint and its saved frozen linear probe. This is post-hoc diagnosis on the existing held-out episodes and simulator banks, not a fresh confirmatory test.

## Three conditions

1. **Original:** original predicted-latent feedback and direct frozen-probe readout. Recompute all physical horizons, fixed-candidate rankings and50 closed-loop episodes. Assert original open-loop metrics and fixed candidate costs agree with retained pilot evidence within numerical tolerance.
2. **Decode→re-encode:** after every prediction, decode to the normalized image and encode that image with the frozen encoder; feed the resulting encoding back into the next predictor context. Apply the existing frozen probe to that encoding. This changes both feedback and readout compatibility. A performance difference measures their combined repair, not a clean isolated feedback-only effect.
3. **Teacher-forced oracle:** for each requested horizon, predict only the last transition from true prior observation history, then decode/re-encode for the same compatible readout. On recorded episodes these are true dataset observations. For candidate ranking/CEM the simulator provides each candidate's true prefix up to the penultimate model step. The final observation/state/cost is not supplied to the prediction. This uses privileged future-prefix information and is not a deployable model-only planner or a fair compute comparison. Report its50-episode results separately as an oracle diagnostic.

## Frozen settings

Same checkpoint, probe,124 test episodes and50 shared simulator candidate banks; history3; frameskip5; goal horizon5; rollout horizon5; execute prefix1;10 replans; CEM64 samples,8 elites,5 iterations; same CEM seeds; no simulator early stop; same physical cost and goal threshold. No adjustment after seeing results. Horizon1/2/4/8/16/32 counts124/124/124/124/106/4. Final and ever-goal attainment remain separate.

Decode outputs already use the encoder's normalized [-1,1] image convention. No extra image rescaling, new fitted decoder, new probe, or retraining. The AdaLN encoder uses visual input only, so no invented predicted proprioception is needed. Source: `study/reencode_control.py`.

## Validation and provenance

- Training SHA `40d8c7840a0a7e96933a42e10c60a926b272430e`.
- Active corrected inference SHA `1e7fbc592d1b44be09cba7a5cc00f83acc0bf3b7`.
- Checkpoint SHA256 `9e1eca55448f073c44ffaf4f0790203767402ffc45d73aeee6bfa169011672f5`.
- Frozen probe SHA256 `bd752782380ef143bd8f2e4cfb96c58b72054dcce502072192c773d30089ed4d`.
- Original attempt `reencode-control-20260915`, SHA `dc054266d15a965090d5a18ba6080e92ce61d26c`, stopped on a tight prefix-consistency assertion before planning. Full future-action encoding introduced shape-dependent numerical differences (max0.044 physical units in the failed comparison). Corrected code encodes only the causal action prefix with consistent layout; tolerance was not loosened. Failed state/log preserved.
- Controller observer initially had an inventory syntax error, corrected before verified observation. It never launches scientific processes.
- H1 teacher/reencode equality, prefix-causality, candidate-order invariance, original baseline reproduction, shared bank hashes, frozen weights/probe, and final checkpoint hash are checked. Failures stop the queue and preserve artifacts; do not silently skip stages.

## Execution and retention

Detached worker command with isolated project Python, from the corrected immutable snapshot:

```bash
python -u -m study.reencode_control --output reencode-control-20260915-r2
```

This documents the active invocation, not permission to launch a duplicate. Project flock guards execution. Each completed bank and current replan/progress are saved. State/artifacts: worker project `artifacts/reencode-control-20260915-r2/`; mirrored controller `/mnt/research/jepa-worldmodel-study-storage/artifacts/reencode-control-20260915-r2/`. Worker log: project `runs/reencode-control-20260915-r2.log`.

Persistent observer `jepa-reencode-r2-monitor.service` uses `scripts/study/worker/watch_control.py`, retains JSON/NPZ outputs and exits on completion/failure. It does not wake Codex or restart failed science. Incomplete stages require reconciliation before recovery; this script does not automatically resume a partially completed stage. No training is authorized by this queue.

## Completion interpretation

Quantify per-horizon error change, ranking regret/correlation and final/ever goal attainment against original. Include teacher-forced oracle results with its privileged-information caveat. Keep numerical execution success separate from scientific performance. After all stages and artifact validation, update the current snapshot and append the final result to research history. Do not launch training until the user has reviewed this result and explicitly authorizes training.
