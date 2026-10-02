#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o noglob
set -o noclobber
set -o posix

usage() {
	printf '%s\n' \
		'Usage: bash brew.sh [--check | --install]' \
		'Default: check the Brewfile without changing installed packages.' \
		'--install: install missing packages without blanket upgrades or cleanup.'
}

if [ "$#" -gt 1 ]; then
	usage >&2
	exit 2
fi

case "${1:---check}" in
	--check) action=check ;;
	--install) action=install ;;
	--help|-h) usage; exit ;;
	*) usage >&2; exit 2 ;;
esac

if ! command -v brew > /dev/null; then
	printf '%s\n' 'Homebrew is required. Install it from https://brew.sh first.' >&2
	exit 1
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
export HOMEBREW_NO_AUTO_UPDATE=1
export HOMEBREW_NO_INSTALL_CLEANUP=1

brew bundle "$action" --file="${script_dir}/Brewfile" --no-upgrade
