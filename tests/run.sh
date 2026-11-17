#!/usr/bin/env bash
set -euo pipefail
STARK_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$STARK_ROOT"
bash -n install.sh uninstall.sh update.sh tests/run.sh
if command -v shellcheck >/dev/null; then
  shellcheck install.sh uninstall.sh update.sh tests/run.sh overlays/stark.system-monitor/discover-sensors.sh
else
  printf '%s\n' 'ShellCheck not installed; Bash syntax checks ran. CI requires ShellCheck.'
fi
python3 -m unittest discover -s tests -p 'test_*.py' -v
if command -v node >/dev/null; then node tests/focus-model.test.js; fi
