# Contributing

Develop in a clean user account or disposable Omarchy VM. Do not develop by
silently changing a user's active desktop. Never edit `/usr/share/omarchy`.

## Checks

```bash
./tests/run.sh
python3 tools/check.py
```

The tests use temporary homes and mock native commands. Bash syntax checks always
run; ShellCheck runs when available and is required in CI. Node runs media matching
regressions. Python's standard library provides the lifecycle tests. These checks
do not establish graphical runtime correctness.

Build complete plugins into a new directory:

```bash
python3 tools/stark_manager.py build --components island,launcher,calendar,visualizer --output .build/review
```

This copies unchanged, hash-verified files from the installed Omarchy package,
applies exact patches, adds overlays, and runs `omarchy plugin validate` for each
complete plugin. It does not activate them. Source overlay folders are incomplete
by design and should not be installed directly.

Make a reviewed change in that staged tree, then capture one file explicitly:

```bash
python3 tools/refresh_patch.py launcher Menu.qml --from-file .build/review/stark.menu/Menu.qml
```

This updates the patch/overlay and expected output hash. It does not change the
upstream source pin. Rebuild into another new directory, run tests, inspect
`git diff`, and update upstream notes and the changelog.

## Review requirements

- Preserve native services, clone routing and default keybindings.
- Avoid new Quickshell processes and unnecessary shell commands.
- Treat network/IPC/file text as untrusted. Use `Text.PlainText` for new display
  sinks, bound parsed input, and add meaningful regression tests.
- Use `Style.duration` and Omarchy motion curves for custom shell animations.
- Keep credentials, monitor names, scaling, locations and interface names out of
  the shared package and screenshots.
- Keep licenses and source version/hash attribution with adapted files.
- Test install twice, update, rollback and uninstall with personal edits present.

Before widening version support or promoting the island to default, complete the
runtime acceptance matrix in [VALIDATION.md](VALIDATION.md), including service-backed
widgets, keyboard navigation, multiple monitors, panel switching and reloads.
