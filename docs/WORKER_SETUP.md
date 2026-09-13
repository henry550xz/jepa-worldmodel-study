# Worker setup (prepared, not executed)

No JEPA alias is configured by this project. Every SSH entry point requires an explicitly confirmed alias. Existing root SSH config is reused read-only with StrictHostKeyChecking=yes and UpdateHostKeys=no. Unknown host keys fail rather than modifying ~/.ssh.

## Environment recommendation
Use a fresh prefix on the worker data volume, never system Python or another project's env. Upstream environment.yaml specifies Python 3.9, conda-forge ffmpeg 4.3.2 and pinned pip dependencies including torch 2.3.0, torchvision 0.18.0, CUDA-12.1 runtime packages, hydra-core 1.2.0, accelerate 0.26.1, decord 0.6.0, pygame 2.5.2 and pymunk 6.8.0. No uv workflow is supplied. OGBench has a separate lpwm_swm/environment.yaml and should stay separate.

Keep Python 3.9 for initial reproduction; networkx 3.2.1 supports it (https://pypi.org/project/networkx/3.2.1/). NumPy is unpinned upstream; add numpy==1.26.4 to a GENERATED worker copy to avoid an uncontrolled NumPy-2 transition with the older compiled stack. This is a disclosed compatibility constraint, not an upstream lock. Keep original environment.yaml untouched. Verify solver output, pip check, imports and dataset decoding before expensive work. Package wheels are not fully hash-locked yet.

PyTorch documents 2.3.0 with torchvision 0.18.0 and a CUDA-12.1 wheel option (https://pytorch.org/get-started/previous-versions/). A 4090 requires a working compatible NVIDIA driver; verify with the worker audit and CUDA allocation smoke. Do not install/change drivers. A failed old ffmpeg solve or import requires a reviewed minimal compatibility patch, not silent upgrades. Conda must already exist at /root/miniconda3/bin/conda; missing conda is an explicit bootstrap blocker.

## Exact deployment sequence once an alias is confirmed
Run from canonical clean checkout; replace CONFIRMED_JEPA_ALIAS and VERIFIED_DATASET_VERSION first.

```bash
JEPA_ALIAS=CONFIRMED_JEPA_ALIAS
SHA=$(git rev-parse HEAD)
bash scripts/study/worker/audit_worker.sh "$JEPA_ALIAS"
bash scripts/study/worker/sync_code_to_worker.sh "$JEPA_ALIAS"
bash scripts/study/worker/setup_worker_env.sh "$JEPA_ALIAS" "$SHA"
# Separately acquire/verify pusht_noise/train and pusht_noise/val on worker datasets/.
bash scripts/study/worker/run_pusht_reproduction.sh "$JEPA_ALIAS" "$SHA" gaussian smoke VERIFIED_DATASET_VERSION
# Inspect manifest/logs and wait for completion before next queue item.
```

setup_worker_env.sh executes `conda env create --prefix <worker-root>/envs/lpwm-<SHA> --file <worker-root>/envs/environment-<SHA>.yaml`, then pip check and a CUDA/import check. Caches, temp builds and conda packages are redirected to the worker data volume. It refuses an existing prefix.

Code is exported from HEAD, hashed and uploaded to code/<SHA>, with no .git, credentials or untracked files. A second deployment of the same SHA refuses to overwrite; inspect incomplete deployments explicitly. The local small staging snapshot is retained under controller storage/runs/deploy.*. Result retrieval never deletes destination files. Checkpoints are intentionally not retrieved by the compact script; select a completed checkpoint explicitly, compare SHA-256 and store under controller storage/checkpoints. Do not destroy the worker before verified recovery state is retained.

The common physical evaluator has metric/probe contracts but no finished simulator/checkpoint adapter yet. Official reproduction planning is separate; it retains upstream coupled horizons and simulator-informed CEM stopping. No result should be labeled a controlled three-arm planning comparison until those adapters are implemented and tested.
