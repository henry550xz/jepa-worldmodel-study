#!/usr/bin/env bash
# Sourced only. No default alias and no automatic worker connection.
set -euo pipefail
JEPA_ALIAS=${1:?explicit confirmed JEPA SSH alias required}
JEPA_WORKER_ROOT=${JEPA_WORKER_ROOT:-/root/autodl-tmp/robotics/jepa-worldmodel-study}
[[ "$JEPA_ALIAS" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || { echo 'Invalid SSH alias' >&2; exit 2; }
[[ "$JEPA_WORKER_ROOT" =~ ^/root/autodl-tmp/[A-Za-z0-9/_-]+$ && "$JEPA_WORKER_ROOT" != *..* ]] || exit 2
SSH=(ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o UpdateHostKeys=no -o ConnectTimeout=20 -o ServerAliveInterval=30 -o ServerAliveCountMax=4)
RSYNC_SSH='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o UpdateHostKeys=no -o ConnectTimeout=20 -o ServerAliveInterval=30 -o ServerAliveCountMax=4'
