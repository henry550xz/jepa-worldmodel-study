#!/usr/bin/env bash
# Worker-only future launcher. Prepared by readiness gate; NOT run by that gate.
set -euo pipefail
[[ ${1:-} == --authorized-full-pilot ]] || { echo 'Full pilot requires explicit user authorization.' >&2; exit 2; }
ROOT=/root/autodl-tmp/robotics/jepa-worldmodel-study
PY="$ROOT/envs/lpwm-5090/bin/python"
[[ $(findmnt -n -o TARGET -T /root/autodl-tmp) != / ]] || exit 2
cd "$(dirname "$0")/../../.."
exec 9>"$ROOT/runs/three-arm-pilot.lock"
flock -n 9 || { echo 'Pilot queue already active' >&2; exit 2; }
# Refuse duplicate/restarted scientific queues; recovery requires manifest inspection.
mkdir "$ROOT/runs/three-arm-pilot-queue"
DATA_VERSION=442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08
for method in pixel gaussian sparse; do
    printf '%s training\n' "$method" > "$ROOT/runs/three-arm-pilot-queue/stage"
    MANIFEST=$("$PY" -m study.run --method "$method" --phase pilot --seed 0 --dataset-version "$DATA_VERSION")
    printf '%s\n' "$MANIFEST" >> "$ROOT/runs/three-arm-pilot-queue/manifests.txt"
    RUN_ID=$(basename "$(dirname "$MANIFEST")")
    printf '%s evaluation\n' "$method" > "$ROOT/runs/three-arm-pilot-queue/stage"
    "$PY" -m study.evaluate_common "$RUN_ID" --profile pilot
    printf '%s complete\n' "$method" >> "$ROOT/runs/three-arm-pilot-queue/completed.txt"
done
printf 'complete\n' > "$ROOT/runs/three-arm-pilot-queue/stage"
