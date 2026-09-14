# Pilot interruption and recovery — 2026-09-14

User confirmed AutoDL balance exhaustion stopped the worker. Connectivity returned at23:00 UTC. GPU idle, no Python training processes; data disk persisted with31G free.

Interrupted source: `fade5b690451efd23d5e428bcf5013c0e32a8aec`.

- Pixel `pixel-s0-20260914T183511-a3085365015f`: last logged step36,109 of115,308.
- Gaussian `gaussian-s0-20260914T183511-682da9f8087f`:35,952.
- Sparse `sparse-s0-20260914T183511-9f2f3d95bfff`:34,526.

All stopped during epoch1. No checkpoint files exist for these attempts; the frozen training implementation saved after epochs. Therefore exact continuation is impossible. Preserve manifests/logs and archive the dead queue; restart all three arms from seed0 with new run IDs. This is recovery from infrastructure interruption, not a repeated completed experiment or a protocol change. No changes to architecture, seeds, batch size, splits, optimizers, update budget or evaluation.

The recovery snapshot differs only in documentation. Interrupted manifests retain their original scientific provenance and are explicitly marked interrupted. Controller observer will follow the new snapshot. Remaining training time resets to approximately10h49m plus validation/checkpoint overhead and unmeasured full common evaluation.

Limitation: another shutdown before an epoch checkpoint can again lose progress. Exact optimizer/RNG/data-position resume is not implemented or validated; do not claim it is. The worker needs sufficient account balance for the full queue.
