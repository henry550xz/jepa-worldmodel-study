#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh" "${1:?confirmed JEPA alias required}"
mountpoint -q /mnt/research || { echo 'Research volume not mounted' >&2; exit 1; }
REPO=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$REPO"
SHA=$(git rev-parse HEAD)
STAGING=$(mktemp -d /mnt/research/jepa-worldmodel-study-storage/runs/deploy.XXXXXXXX)
# Retain the small staged snapshot for traceability; never use controller HOME as source.
python3 -m study.snapshot "$STAGING/snapshot"
"${SSH[@]}" "$JEPA_ALIAS" "bash -s -- '$JEPA_WORKER_ROOT' '$SHA'" <<'REMOTE'
set -euo pipefail
ROOT=$1; SHA=$2
[[ $(findmnt -n -o TARGET -T /root/autodl-tmp) != / ]] || { echo 'Worker data disk absent' >&2; exit 1; }
mkdir -p "$ROOT"/{code,envs,datasets,caches,checkpoints,artifacts,runs}
# Refuse to overwrite a deployed commit or a running job's source.
mkdir "$ROOT/code/$SHA"
REMOTE
rsync -az --safe-links -e "$RSYNC_SSH" "$STAGING/snapshot/" "$JEPA_ALIAS:$JEPA_WORKER_ROOT/code/$SHA/"
printf 'Deployed commit %s to %s:%s/code/%s\n' "$SHA" "$JEPA_ALIAS" "$JEPA_WORKER_ROOT" "$SHA"
