# Current project status

## PILOT_READY — readiness gate complete

**No full three-method research pilot has been launched. Await explicit user authorization.**

Authoritative readiness report: [PILOT_READINESS_REPORT.md](PILOT_READINESS_REPORT.md). Protocol: [PILOT_READINESS_PROTOCOL.md](PILOT_READINESS_PROTOCOL.md). Original reproduction report: [UPSTREAM_REPRODUCTION_REPORT.md](UPSTREAM_REPRODUCTION_REPORT.md).

- Canonical checkout: `/mnt/research/robotics/jepa-worldmodel-study`, branch `study/pixel-baseline`; storage `/mnt/research/jepa-worldmodel-study-storage`. Research mount verified before writes.
- Initial upstream/main: `bdd812d9432cccda8c350086006401b436f91982`, tag `baseline/upstream-initial`. Origin `henry550xz/jepa-worldmodel-study`; upstream `YilunKuang/lpworldmodel`. Current documentation HEAD may be newer than validated experiment snapshots.
- Validated matched-training snapshot: `8d8b123c6d9c05b11099ef23556f5e9159c8e424`; final evaluator: `a3497a5210af0850133098ae85082231f64304f7`; prepared launch snapshot: `6c70470ff0bb412b6892b2126ef4f550bfb4b6bb` (same scientific code plus guarded launcher).
- Frozen partitions: world train17,405 / world validation512 / probe train512 / validation128 / untouched test124 / readiness fixtures4 / reserved upstream validation21. Simulator readiness and pilot seeds are separate. Training/probe-fit memberships are unchanged from the smoke checkpoint snapshot; readiness fixtures are excluded from future test use.
- Real checkpoints and simulator replay adapters validated for all three methods. Both frozen probe types, physical horizon1/2/4/8/16/32 metrics, causal rollout prefixes, fixed-candidate ranking/order invariance and matched CEM planning passed.
- Bounded training:8 updates plus2 validation batches per arm, batch32 FP32. Pixel peak allocated/reserved7.701/8.313GiB; Gaussian/Sparse7.810/8.131GiB. Timed steady compute throughput approximately353/304/308 windows/s respectively (excludes loader waits/startup; short measurement).
-29 worker tests passed. Readiness models are undertrained plumbing fixtures; their physical scores are not scientific comparisons. Constant probe-training dimensions are masked for every method to avoid unidentifiable readout amplification. See report for all compatibility fixes and preserved earlier failures.
- Recommend16GiB+ VRAM for this exact matched configuration; only RTX5090 tested.24GiB allows extra margin. Original batch64 reproduction diagnostics required near29GiB and are not the new matched diagnostic path.

## Readiness artifacts

- Pixel: `pixel-s0-20260914T175035-f1c2ddfbd50d`.
- Gaussian: `gaussian-s0-20260914T175059-72dc6978657d`.
- Sparse: `sparse-s0-20260914T175123-f919227298f8`.
- Controller compact evidence: storage `runs/<run>/`, final `common-readiness-a3497a5210af/` including probe weights and candidate scores. Aggregate: `runs/PILOT_READINESS_RESULTS.json`. Frozen bank: `artifacts/physical-candidates-v2-910001.npz`.
- Readiness checkpoints remain on the worker. Original Gaussian and sparse reproduction checkpoints are retained and hash-verified on controller.

## Worker and environment

Worker `autodl-jepa`, RTX5090, currently idle; no active readiness or research training job. Worker remains provisioned. Workspace `/root/autodl-tmp/robotics/jepa-worldmodel-study/`; data disk20G used/31G free, root54M used at final audit.

Dedicated `envs/lpwm-5090/bin/python`: Python3.12.3, PyTorch2.8.0+cu128, CUDA runtime12.8; no base packages/drivers modified. Upstream compatibility choices and environment specification remain in manifests/conf/study and the reproduction report. Official PushT archive SHA256 `442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08`; dataset `datasets/pusht_noise` under worker data volume.

## Completed upstream reproduction

Immutable reproduction code `0f1720a0be0c73a98a16ce48936c052d7aaee3a6`: Gaussian72% (36/50), Sparse80% (40/50), both training seed0 and planning seed99. Queue complete; systemd `jepa-reproduction-queue.service` exited successfully. Results validate execution, not a general sparse advantage or exact agreement with an established paper target.

## Next action / boundaries

Review the readiness report and exact proposed launch commands. `scripts/study/worker/run_three_arm_pilot.sh` is prepared but unlaunched; it requires explicit full-pilot authorization, runs all three arms sequentially with common evaluation, rejects duplicate queues and stops on failure. No pixel research pilot or larger sweep is authorized yet.

We are testing WHETHER and WHEN JEPA helps. Equal supervised physical readouts are supplied to all arms; native RGB-cost versus latent-cost planning would be a separate comparison. Common pilot evaluation's larger episode/candidate workload is configured but not run by readiness. Full-epoch throughput and learning quality remain future measurements, not readiness claims.

Use persistent background queues rather than tmux. Repair recoverable infrastructure failures safely; do not repeat completed science. Keep live progress in queue state/session reports; update this handoff at goal completion only. When remaining ETA is below5 minutes, stay to verify completion and report.
