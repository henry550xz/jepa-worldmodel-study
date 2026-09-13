# Current project status

## Validated setup
- Canonical checkout `/mnt/research/robotics/jepa-worldmodel-study` on verified mounted research disk.
- GitHub fork henry550xz/jepa-worldmodel-study verified parent YilunKuang/lpworldmodel.
- Baseline bdd812d9432cccda8c350086006401b436f91982; annotated baseline/upstream-initial; main unchanged.
- Common foundation committed through 01f2126 on study/common-eval. Pixel implementation isolated on study/pixel-baseline, committed through 974d210 (before this status update). Exact current SHA: `git rev-parse HEAD`; each deployment/run records an immutable SHA.
- Code map, protocol, metric/probe scaffold and committed-snapshot deployment scripts exist.
- Controller checks: 10 passed, Torch module skipped (no controller PyTorch). No heavyweight controller installation.

## Worker update
User explicitly authorized autodl-jepa. Audit confirms RTX 5090, driver 595.71.05, base Python 3.12.3, torch 2.8.0+cu128, torchvision .23.0+cu128. Data disk is xfs /dev/md0, 50G at /root/autodl-tmp, empty at audit. Root overlay 30G; do not install there. Tsinghua, Aliyun, PyPI, OSF API and PyTorch wheel HEAD requests returned 200 within ~0.4–1.5 seconds.

## Environment decision / deviations
Do not downgrade the functioning Blackwell CUDA stack to upstream torch2.3/cu121. Create data-disk venv `envs/lpwm-5090` with read-only system-site-packages inheritance from base; pip writes only to venv. This deliberately uses Python3.12 instead of upstream3.9, after auditing the imported PushT path. Upgrade Hydra1.2->1.3.2, W&B .13.1->.17.9 and scikit-image .19.3->.24 for compatibility; override NumPy2.3.2 with1.26.4 locally. Torch/torchvision constrained to existing versions. Remaining targeted dependencies are pinned. Do not install the full export's unused old transformers/tokenizers stack.

Trusted upstream dataset/checkpoint loading uses TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 for the PyTorch2.6+ default change; only verified official data and self-generated checkpoints may be loaded. Environment is not yet validated; no reproduction result exists.

## Scientific status and gates
- Dense/sparse reproduction: NOT RUN. Exact official cells documented; new runner records config/provenance/telemetry.
- Pixel: implemented independently but NOT launched; Torch correctness gates unvalidated. Pixel will not interfere with official upstream runs.
- Evaluator: physical metrics/ranking and frozen probe infrastructure implemented; simulator/checkpoint adapters and frozen episode partitions not finished.
- Next: isolated environment/import/CUDA smoke and official PushT acquisition; then Gaussian tiny smoke, sparse tiny smoke, official Gaussian training+planning, official sparse training+planning sequentially.
- Blockers: dependency compatibility, data transfer/footprint, full GPU correctness and VRAM remain unvalidated. No claims of JEPA advantage or upstream metric reproduction.
