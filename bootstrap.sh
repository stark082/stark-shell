#!/usr/bin/env bash
# One-line bootstrap for Stark Shell.
#
# Preview without changing the desktop:
#   curl -fsSL https://raw.githubusercontent.com/stark082/stark-shell/main/bootstrap.sh | bash -s -- --dry-run
#
# Install (default: standalone visualizer):
#   curl -fsSL https://raw.githubusercontent.com/stark082/stark-shell/main/bootstrap.sh | bash
#
# Opt into components:
#   curl -fsSL https://raw.githubusercontent.com/stark082/stark-shell/main/bootstrap.sh | bash -s -- --components island,launcher,calendar,visualizer
#
# Environment overrides: STARK_REPO, STARK_BRANCH, STARK_SHARE.
set -euo pipefail

STARK_REPO="${STARK_REPO:-https://github.com/stark082/stark-shell.git}"
STARK_BRANCH="${STARK_BRANCH:-main}"
STARK_SHARE="${STARK_SHARE:-${XDG_DATA_HOME:-$HOME/.local/share}/stark-shell}"

fail() {
    echo "stark-bootstrap: $*" >&2
    exit 1
}

command -v git >/dev/null 2>&1 || fail "git is required"
command -v python3 >/dev/null 2>&1 || fail "python3 (3.10+) is required"

if [ -d "$STARK_SHARE/.git" ]; then
    if [ -n "$(git -C "$STARK_SHARE" status --porcelain)" ]; then
        fail "existing checkout $STARK_SHARE has local changes; resolve them or remove the folder"
    fi
    echo "==> Updating existing checkout in $STARK_SHARE"
    git -C "$STARK_SHARE" fetch --depth 1 origin "$STARK_BRANCH"
    git -C "$STARK_SHARE" merge --ff-only FETCH_HEAD
else
    echo "==> Cloning Stark Shell into $STARK_SHARE"
    git clone --depth 1 --branch "$STARK_BRANCH" "$STARK_REPO" "$STARK_SHARE"
fi

echo "==> Running installer from $STARK_SHARE (add --dry-run to preview)"
exec "$STARK_SHARE/install.sh" "$@"
