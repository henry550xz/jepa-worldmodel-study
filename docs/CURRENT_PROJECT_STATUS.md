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

Trusted upstream dataset/checkpoint loading uses TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 for the PyTorch2.6+ default change; only verified official data and self-generated checkpoints may be loaded. Environment validated: pip check, train/plan imports, PushT reset, CUDA attention forward/backward all passed. Worker correctness suite: 21 passed in 3.82s. No reproduction result exists yet. Effective package inventory is in manifests/WORKER_ENVIRONMENT_5090.json. Base remains numpy2.3.2/torch2.8+cu128 unchanged; project venv uses numpy1.26.4.

## Scientific status and gates
- Dense/sparse reproduction: NOT RUN. Exact official cells documented; new runner records config/provenance/telemetry.
- Pixel: implemented independently but NOT launched as a research experiment; CPU Torch gradient/causality/action/overfit gates passed on the worker. Pixel will not interfere with official upstream runs.
- Evaluator: physical metrics/ranking and frozen probe infrastructure implemented; simulator/checkpoint adapters and frozen episode partitions not finished.
- Next: isolated environment/import/CUDA smoke and official PushT acquisition; then Gaussian tiny smoke, sparse tiny smoke, official Gaussian training+planning, official sparse training+planning sequentially.
- Blockers: official 2.79GB PushT archive downloading with bounded parallel ranges; official SHA256 recorded in acquisition script. Extraction, dataset GPU smoke and full-batch VRAM still pending. No claims of JEPA advantage or upstream metric reproduction.

- Validated environment/deployment code SHA for upcoming smokes: 3e279431fc0b2db7467ecb99783750c8ba741bc3. Later documentation commits do not change this immutable snapshot.

## First smoke diagnostic
Gaussian smoke gaussian-s0-20260913T213854-88274e66f0ca failed BEFORE model construction (0 GPU allocated bytes). Imported train.main made Hydra treat conf as an importable package; upstream conf/ has no __init__.py. Instrumentation now explicitly passes the absolute config path, preserving upstream config contents. No scientific training result was produced; failed manifest retained.
