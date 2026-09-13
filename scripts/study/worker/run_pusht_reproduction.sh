#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh" "${1:?confirmed JEPA alias required}"
SHA=${2:?deployed SHA required}; METHOD=${3:?gaussian or sparse or pixel}; PHASE=${4:-reproduction}
DATA_VERSION=${5:?dataset version or verified inventory SHA required}
[[ "$SHA" =~ ^[0-9a-f]{40}$ && "$METHOD" =~ ^(gaussian|sparse|pixel)$ && "$PHASE" =~ ^(smoke|reproduction|pilot)$ ]] || exit 2
[[ "$DATA_VERSION" =~ ^[A-Za-z0-9._-]+$ ]] || exit 2
"${SSH[@]}" "$JEPA_ALIAS" "bash -s -- '$JEPA_WORKER_ROOT' '$SHA' '$METHOD' '$PHASE' '$DATA_VERSION'" <<'REMOTE'
set -euo pipefail
ROOT=$1; SHA=$2; METHOD=$3; PHASE=$4; VERSION=$5
cd "$ROOT/code/$SHA"
PYTHON="$ROOT/envs/lpwm-$SHA/bin/python"
# This entry point waits for completion. For long jobs, invoke it in controller tmux;
# worker run state/manifest still survives a terminal disconnect via nohup below.
LOG="$ROOT/runs/launch-$METHOD-$(date -u +%Y%m%dT%H%M%S)-$$.log"
nohup "$PYTHON" -m study.run --method "$METHOD" --phase "$PHASE" --worker-root "$ROOT" --dataset-version "$VERSION" >"$LOG" 2>&1 < /dev/null &
printf 'PID=%s launch_log=%s\n' "$!" "$LOG"
REMOTE
