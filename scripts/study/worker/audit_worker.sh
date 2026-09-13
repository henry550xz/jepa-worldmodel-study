#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh" "${1:?confirmed JEPA alias required}"
"${SSH[@]}" "$JEPA_ALIAS" 'bash -s' <<'REMOTE'
set -euo pipefail
printf 'Worker storage\n'
df -hT / /root/autodl-tmp
findmnt -T /root/autodl-tmp
printf 'GPU and driver\n'
nvidia-smi --query-gpu=name,driver_version,memory.total,memory.free --format=csv
printf 'Tools\n'
for tool in python3 conda rsync tmux nohup; do command -v "$tool" || true; done
if test -x /root/miniconda3/bin/conda; then /root/miniconda3/bin/conda --version; fi
printf 'Persistent-volume candidates\n'
for path in /root/autodl-fs /root/autodl-pub; do test ! -e "$path" || findmnt -T "$path"; done
REMOTE
