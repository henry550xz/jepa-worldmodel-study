#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh" "${1:?confirmed JEPA alias required}"
SHA=${2:?deployed 40-character commit SHA required}
[[ "$SHA" =~ ^[0-9a-f]{40}$ ]] || exit 2
"${SSH[@]}" "$JEPA_ALIAS" "bash -s -- '$JEPA_WORKER_ROOT' '$SHA'" <<'REMOTE'
set -euo pipefail
ROOT=$1; SHA=$2
[[ $(findmnt -n -o TARGET -T /root/autodl-tmp) != / ]] || exit 1
BASE=/root/miniconda3/bin/python
"$BASE" - <<'PY'
import torch, torchvision, sys
assert sys.version_info[:2] == (3,12)
assert torch.__version__ == '2.8.0+cu128'
assert torchvision.__version__ == '0.23.0+cu128'
assert torch.cuda.is_available()
print('Verified existing Blackwell-capable torch',torch.__version__)
PY
PREFIX="$ROOT/envs/lpwm-5090"
[[ ! -e "$PREFIX" ]] || { echo 'Refusing to modify existing environment' >&2; exit 1; }
export PIP_CACHE_DIR="$ROOT/caches/pip" TMPDIR="$ROOT/caches/tmp" PIP_DISABLE_PIP_VERSION_CHECK=1
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$TMPDIR"
# Read-only inheritance avoids reinstalling working multi-GB CUDA packages.
# All project additions/overrides go into this data-volume venv, never base.
"$BASE" -m venv --system-site-packages "$PREFIX"
"$PREFIX/bin/python" -m pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
 --timeout 20 --retries 1 \
 -c "$ROOT/code/$SHA/conf/study/worker-5090-constraints.txt" \
 -r "$ROOT/code/$SHA/conf/study/worker-5090-requirements.txt"
"$PREFIX/bin/python" -m pip check
"$PREFIX/bin/python" - "$ROOT/envs/packages-$SHA.json" <<'PY'
import importlib.metadata as m, json, sys, torch, torchvision, hydra, decord, pygame, pymunk
from pathlib import Path
assert torch.cuda.is_available()
a=torch.randn(64,64,device='cuda'); (a@a).sum().item()
print('Python',sys.version.split()[0],'torch',torch.__version__,'CUDA',torch.version.cuda)
print('GPU',torch.cuda.get_device_name(0),'prefix',sys.prefix)
Path(sys.argv[1]).write_text(json.dumps(sorted((d.metadata['Name'],d.version) for d in m.distributions()),indent=2))
PY
REMOTE
