#!/usr/bin/env bash
if [ -n "${ZSH_VERSION:-}" ] || [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
    printf '%s\n' 'Run ./sync-back.sh as an executable; do not source it.' >&2
    return 1
fi
set -euo pipefail

DOTFILES_ROOT=$(cd -- "$(dirname -- "$0")" && pwd)
exec /usr/bin/python3 -B "$DOTFILES_ROOT/scripts/dotfiles.py" capture "$@"
