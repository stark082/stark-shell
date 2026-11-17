# Testing

```bash
./tests/run.sh
python3 tools/check.py
python3 -m compileall -q tools tests
luac -p hypr/stark-animations.lua
```

The runner checks Bash syntax, runs ShellCheck when installed, Python unittest
lifecycle/bootstrap regressions, and Node media-focus cases when available.
CI requires ShellCheck and also runs Ruff's Python correctness checks.
No dependency download or live desktop configuration mutation is needed.

Current local integration run: 67 Python tests and six media-focus cases passed.
Package consistency passed (19 JSON files, 14 component blueprints and font hashes).
All 14 components built against the installed Omarchy 4.5.0-3 sources and passed
the native validator; Qt qmlformat parsed all 53 materialized QML files.
Lua syntax, Python compilation, Python 3.10 grammar, and diff whitespace checks
passed. ShellCheck 0.11.0 passed using an existing cached binary in /tmp.
Ruff was unavailable locally; CI results are not claimed.

One test uses the actual bundled font files and real fc-cache/fc-match with a
private Fontconfig configuration and cache inside temporary storage. Package
installation tests mock subprocess calls and never invoke real sudo/pacman.
All lifecycle tests use HOME paths containing spaces, ampersand and dollar signs.

Mocks cover fresh/repeated/custom installation, upgrade, dependency/version
failures, conflicts, rollback/recovery, symlink destinations, invalid components,
malformed configuration, font integrity/application/restoration/reuse, dependency
consent/decline/failure, root refusal, profiles, activation failure, reactivation,
dry runs, and bootstrap download/integrity
failure. They cannot establish native IPC, rendering or compositor behavior.
Bootstrap network failure is simulated, not a real GitHub availability test.

Use [the graphical acceptance matrix](VALIDATION.md) before stable publication.
Historical results there are not a substitute for rerunning this candidate.

A real-account standard+fonts dry run stopped at the existing unmanaged stark.bar
prototype, as intended. Read-only compositor/shell IPC works outside the sandbox.
No live candidate installation, restart, package installation, or graphical
acceptance was performed: the owner requested approval before such actions.
The running prototype is not evidence that this candidate was graphically tested.
