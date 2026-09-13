#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh" "${1:?confirmed JEPA alias required}"
SHA=${2:?deployed 40-character commit SHA required}
[[ "$SHA" =~ ^[0-9a-f]{40}$ ]] || exit 2
"${SSH[@]}" "$JEPA_ALIAS" "bash -s -- '$JEPA_WORKER_ROOT' '$SHA'" <<'REMOTE'
set -euo pipefail
ROOT=$1; SHA=$2
[[ $(findmnt -n -o TARGET -T /root/autodl-tmp) != / ]] || exit 1
CONDA=/root/miniconda3/bin/conda
[[ -x "$CONDA" ]] || { echo 'Conda missing: environment bootstrap needs a reviewed installer' >&2; exit 1; }
PREFIX="$ROOT/envs/lpwm-$SHA"
[[ ! -e "$PREFIX" ]] || { echo 'Refusing to modify existing environment' >&2; exit 1; }
export CONDA_PKGS_DIRS="$ROOT/caches/conda-pkgs" PIP_CACHE_DIR="$ROOT/caches/pip" TMPDIR="$ROOT/caches/tmp"
mkdir -p "$TMPDIR"
# Preserve upstream export; generate a worker copy with the one disclosed extra pin.
python3 - "$ROOT/code/$SHA/environment.yaml" "$ROOT/envs/environment-$SHA.yaml" <<'PY'
from pathlib import Path
import sys
s=Path(sys.argv[1]).read_text()
assert '  - pip:\n' in s
Path(sys.argv[2]).write_text(s.replace('  - pip:\n','  - pip:\n      - numpy==1.26.4\n',1))
PY
"$CONDA" env create --prefix "$PREFIX" --file "$ROOT/envs/environment-$SHA.yaml"
"$PREFIX/bin/python" -m pip check
"$PREFIX/bin/python" - <<'PY'
import torch, torchvision, hydra, decord, pygame, pymunk
assert torch.cuda.is_available(), 'CUDA unavailable'
print('torch', torch.__version__, 'CUDA runtime', torch.version.cuda)
print('GPU', torch.cuda.get_device_name(0))
PY
# Version inventory only: do not dump environment variables or credential-bearing pip URLs.
"$PREFIX/bin/python" - "$ROOT/envs/packages-$SHA.json" <<'PY'
import importlib.metadata as m, json, sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps(sorted((d.metadata['Name'],d.version) for d in m.distributions()),indent=2))
PY
REMOTE
