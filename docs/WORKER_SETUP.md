# Confirmed RTX 5090 worker setup

User authorized `autodl-jepa`. Every SSH script still requires an explicit alias. SSH config is reused read-only with StrictHostKeyChecking=yes and UpdateHostKeys=no; neither host keys nor aliases are rewritten.

## Validated environment
- Worker data disk: `/root/autodl-tmp`, xfs, 50G; root overlay 30G.
- Driver 595.71.05; RTX5090, 32607 MiB; existing torch2.8.0+cu128 / torchvision0.23.0+cu128, CUDA runtime12.8. Do not downgrade to upstream torch2.3/cu121 on this GPU.
- Dedicated `/root/autodl-tmp/robotics/jepa-worldmodel-study/envs/lpwm-5090` is a Python3.12.3 venv with `--system-site-packages`, created using `/root/miniconda3/bin/python`. It reads base torch/CUDA packages without modifying base; project additions and NumPy override live on the data disk. Environment size after install: 664M. Root remained53M.
- Targeted requirements and constraints: `conf/study/worker-5090-{requirements,constraints}.txt`. Setup downloads from Tsinghua; bounded connectivity checks found Tsinghua/Aliyun/PyPI/OSF/PyTorch endpoints reachable. No CUDA package was downloaded/replaced. All pip caches and build temp files are on the data disk.
- pip check passed; train.py/plan.py import; PushT reset returns state(7), image(224,224,3); CUDA SDPA forward/backward passed. Worker tests:21 passed in3.82s.

## Disclosed compatibility deviations
Upstream's broad environment.yaml expects Python3.9, torch2.3.0, torchvision.18.0, hydra1.2.0 and many unrelated packages. For current Blackwell worker, preserve Python3.12.3 and installed torch2.8/cu128 read-only. Hydra1.3.2, W&B.17.9 and scikit-image.24 are compatible replacements for older upstream pins. NumPy is pinned locally to1.26.4 (upstream unpinned, base2.3.2). Main physics/data dependencies retain upstream pins. Matplotlib/Pillow inherit newer base versions. Old unused transformers/tokenizers and OGBench dependencies are not installed.

This is an explicitly tested compatibility environment, not an exact recreation of the paper's software stack. Preserve the installed package inventory with results. `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1` restores historical torch.load semantics ONLY for the hash-verified official archive and self-generated checkpoints. Never use this with untrusted downloads. Driver capability13.2 is not the PyTorch runtime; actual runtime is12.8.

## Deployment / run commands
```bash
JEPA_ALIAS=autodl-jepa
SHA=$(git rev-parse HEAD)
bash scripts/study/worker/audit_worker.sh "$JEPA_ALIAS"
bash scripts/study/worker/sync_code_to_worker.sh "$JEPA_ALIAS"
# Fresh worker only: refuses to overwrite existing envs/lpwm-5090.
bash scripts/study/worker/setup_worker_env.sh "$JEPA_ALIAS" "$SHA"
# Dataset acquisition runs on worker: python -m study.acquire_pusht
bash scripts/study/worker/run_pusht_reproduction.sh "$JEPA_ALIAS" "$SHA" gaussian smoke 442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08
```
Use full SHA snapshot directories `code/<SHA>`. Each snapshot contains hashes and has no .git, credentials or untracked files. Repeat deployment of a SHA refuses overwrite. Environments are independent of code SHA and must not be modified during the paired reproductions.

After a completed reproduction training run, invoke in that SAME worker snapshot:
```bash
/root/autodl-tmp/robotics/jepa-worldmodel-study/envs/lpwm-5090/bin/python -m study.plan_official RUN_ID
```
Run the next queue item only after reviewing the preceding manifest. The official evaluator retains 50 episodes, seed99, goal/rollout/prefix5, CEM300/30/30 and max10 replans. It is not the common controlled evaluator. Model-only latency is not currently separated from simulator/video overhead; measured evaluation wall time is explicitly labeled end-to-end.

Compact retrieval uses sync_compact_results_back.sh ALIAS RUN_ID; never --delete. Checkpoints remain separate and must be selected and SHA-verified before retention. No automatic checkpoint purge. Instance-local data remain at risk until copied to controller or independent durable storage.
