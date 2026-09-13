#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh" "${1:?confirmed JEPA alias required}"
RUN_ID=${2:?exact run ID required}
[[ "$RUN_ID" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ && "$RUN_ID" != *..* ]] || exit 2
mountpoint -q /mnt/research || exit 1
DEST="/mnt/research/jepa-worldmodel-study-storage/runs/$RUN_ID"
mkdir -p "$DEST"
# Runs contain logs/configs/telemetry, not checkpoints. Explicit extension allowlist.
rsync -az --partial --max-size=20m --safe-links -e "$RSYNC_SSH" \
  --exclude='.env*' --exclude='environment.txt' --exclude='wandb/' \
  --include='*/' --include='*.json' --include='*.yaml' --include='*.csv' --include='*.log' \
  --exclude='*' "$JEPA_ALIAS:$JEPA_WORKER_ROOT/runs/$RUN_ID/" "$DEST/"
