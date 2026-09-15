#!/usr/bin/env bash
set -euo pipefail
[[ ${1:-} == --authorized-full ]] || exit 2
ROOT=/root/autodl-tmp/robotics/jepa-worldmodel-study
[[ $(findmnt -n -o TARGET -T /root/autodl-tmp) != / ]] || exit 2
cd "$(dirname "$0")/../../.."
export PYTHONDONTWRITEBYTECODE=1
exec "$ROOT/envs/lpwm-5090/bin/python" -u -m study.mechanism_queue --authorized-full --output "${2:?queue id required}"
