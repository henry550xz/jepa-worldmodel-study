# PILOT_READY

Pilot-readiness gate complete. No full three-arm research training was launched. Readiness means validated execution and shared evaluation contracts; it does not mean the eight-update models are accurate.

## Validated gates

- Frozen world train17,405 / world validation512 / probe train512 / probe validation128 / probe test124 / reserved readiness test4 / upstream validation21 episodes. World and probe fitting memberships are unchanged from the training-smoke snapshot; four preselected long episodes were reserved from future test use.
- All three committed-checkpoint adapters loaded real eight-update checkpoints. Frozen linear and MLP probes, physical horizons1/2/4/8/16/32, true-encoding versus predicted-encoding errors, causal rollout prefixes, fixed-candidate ranking/order invariance and two closed-loop replans passed.
- Same bank SHA256, identical episode/frame selections and physical metrics across all arms. Candidate replay checked against reset plus executed prefix; oracle ranking has zero regret. Same physical-probe cost and CEM budget320 candidate evaluations/replan,64 samples,8 elites,5 iterations, rollout5, execute1, no simulator-informed stopping.
-29 worker tests passed (including gradient/causality/action/overfit/probe/metric/provenance tests); controller15 passed with Torch-dependent tests skipped. Failed exploratory checks and their logs are preserved; final results use only the corrected evaluator.

## Measured matched configuration

FP32,224px,history3,frameskip5,batch32; eight optimizer updates plus two validation batches per arm. Throughput below is windows/s from timed optimizer steps3–8, excluding data-loader waits, startup and validation. It is a short compute-throughput estimate, not full-epoch throughput. Upstream expensive plotting/rollout diagnostics are disabled equally across arms.

| Arm | Peak training allocated GiB | Peak training reserved GiB | Steady windows/s | Bounded training process wall s | Common evaluation wall s | CEM seconds/replan |
|---|---:|---:|---:|---:|---:|---:|
| pixel | 7.701 | 8.312 | 352.8 | 19.31 | 10.01 | 1.301 |
| gaussian | 7.810 | 8.131 | 304.0 | 19.18 | 9.72 | 1.429 |
| sparse | 7.810 | 8.131 | 308.1 | 18.38 | 10.17 | 1.447 |

**GPU recommendation:16 GiB VRAM or more for this exact configuration.** Maximum measured reserved training memory8.313GiB; checkpoint loading stayed below0.72GiB allocated and bounded evaluation below0.27GiB. Only RTX5090 was tested;16GiB is a headroom-based recommendation, not a cross-GPU certification.24GiB offers room for larger batches/candidate chunks.8GiB is insufficient. These figures do not cover the upstream batch64 plus diagnostic path that peaked near29GiB.

## Scientific limits and fixes

- Eight-update networks and small probes are plumbing fixtures. Their scores must not be interpreted as a method comparison or expected pilot accuracy. Full pilot evaluation is configured but not run:512/128 probe fitting episodes,124 held-out test episodes with explicit horizon skips,50 simulator seeds and10 replans.
- Constant probe-training features are masked identically across arms, avoiding arbitrary random readout amplification of previously inactive sparse dimensions. Sparse smoke had197/384 identifiable features; Gaussian/Pixel384/384. Training-only normalizers and masks are shared between true and predicted encodings.
- Pixel uses the same physical readout planning interface as JEPA, with equal labeled probe supervision and the same physical goal input. This is a controlled physical-readout planning comparison, not native RGB-cost versus latent-cost planning. Pixel adds1,237,843 decoder parameters; its temporal RGB loss reaches encoder/dynamics/decoder. No claim of equal compute or optimal pixel architecture is made.
- Compatibility fixes: action gradients checked after AdaLN-zero warmup; guarded upstream subset unpickling; nonfluent upstream eval() support; contiguous reordered NumPy candidate arrays. No upstream model source or existing reproduction artifacts changed.
- Single-image probes report pusher/block positions and circular angle, not velocity. Arbitrary dataset state reset is not claimed exact; candidates use simulator reset/replay. Fixed upstream action-normalization constants remain a disclosed convention.
- Worker is idle and remains provisioned. Worker root54M used; data disk20G used/31G free at final audit. Readiness checkpoints remain worker-side; compact evidence, probe weights and frozen candidate bank are retained on controller storage. Both original reproduction checkpoints remain hash-verified on controller.

## Provenance and artifacts

- Training snapshot: `8d8b123c6d9c05b11099ef23556f5e9159c8e424`. Final evaluator: `a3497a5210af0850133098ae85082231f64304f7`. Prepared deployment (same tested scientific code plus guarded launcher): `6c70470ff0bb412b6892b2126ef4f550bfb4b6bb`.
- Environment: Python3.12.3 / PyTorch2.8.0+cu128 / CUDA runtime12.8 / RTX5090; existing isolated env unchanged.
- Machine-readable evidence: `/mnt/research/jepa-worldmodel-study-storage/runs/PILOT_READINESS_RESULTS.json`. Each run retains manifests, resolved training config, measured telemetry and `common-readiness-a3497a5210af/` results/probes/candidate scores.
- Partition SHA256: `69594de7b00defca169abef54c1e9d2e9e1910ed7ef81e66e3dfa00a67478d4e`.
- Candidate bank SHA256: `0206bf565f8087506453ba915f5d17f64df4bfbba8a10881bc5da8f1f5f084d1`.

## Exact proposed three-arm commands — NOT executed

On `autodl-jepa`, after explicit full-pilot authorization:
```bash
cd /root/autodl-tmp/robotics/jepa-worldmodel-study/code/6c70470ff0bb412b6892b2126ef4f550bfb4b6bb
PY=/root/autodl-tmp/robotics/jepa-worldmodel-study/envs/lpwm-5090/bin/python
DATA_SHA=442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08
"$PY" -m study.run --method pixel --phase pilot --seed 0 --dataset-version "$DATA_SHA"
"$PY" -m study.run --method gaussian --phase pilot --seed 0 --dataset-version "$DATA_SHA"
"$PY" -m study.run --method sparse --phase pilot --seed 0 --dataset-version "$DATA_SHA"
```
The persistent launcher executes these stages sequentially and evaluates each completed run with `python -m study.evaluate_common RUN_ID --profile pilot`. Use it instead of leaving an interactive session open; do not also run the individual commands:
```bash
cd /root/autodl-tmp/robotics/jepa-worldmodel-study/code/6c70470ff0bb412b6892b2126ef4f550bfb4b6bb
nohup bash scripts/study/worker/run_three_arm_pilot.sh --authorized-full-pilot > /root/autodl-tmp/robotics/jepa-worldmodel-study/runs/three-arm-pilot-launch.log 2>&1 < /dev/null &
```
The launcher is prepared only. It refuses duplicate queues and stops on any failed stage. Full-pilot execution awaits user authorization.
