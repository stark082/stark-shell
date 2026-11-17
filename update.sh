#!/usr/bin/env bash
set -euo pipefail
STARK_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$STARK_ROOT/tools/stark_manager.py" "update" "$@"
