# Stark Shell

A portable, reversible set of Omarchy Quattro plugins for Quickshell and Hyprland.
Stark builds on Omarchy's existing shell process, services, widgets, and shortcuts.
It does not install another desktop or launch a second shell.

**0.1.0 is a conservative first release.** The default installation adds only the
media visualizer to the built-in bar. The expanding island and its integrated
launcher/panels are explicit opt-ins, preserved from the working Stark prototype.
The packaged island has been built and statically validated; a clean-account
runtime acceptance pass is still required before calling it production-tested.

## Features

- Audio-reactive five-bar visualization, with CAVA and a PipeWire fallback.
- Media-window focus, including dedicated Omarchy web apps. Normal browser tab
  selection is not available without browser integration; no extension is installed.
- Optional expanding central island with theme colors and automatically centered widgets.
- Optional keyboard-driven island launcher, with a list-based Apps provider.
- Optional native calendar, audio, network, Bluetooth, display, battery, weather,
  world-clock, agent, Wi-Fi QR, and system-monitor integrations.
- Preserves existing widget placement/settings when replacing their native clones.
- Keeps Omarchy clipboard, reminders, tray, and other service-backed functionality
  with the native shell. No replacement keybindings are installed.
- Optional Shantell Sans font assets and isolated Hyprland animation overrides.
- Backups, dry runs, source compatibility checks, receipts, rollback and conservative uninstall.

Dock redesign and a unified control center are **future modules**. The removed
prototype control center is not shipped. The existing Omarchy dock remains native.

## Requirements

Initial compatibility target: **Omarchy 4.5.x, Omarchy's Quickshell 0.3.2, Hyprland
0.56.x**, Python 3.10+, Bash, jq, patch and a running Omarchy shell. Integrated
clones additionally require exact matching source hashes from package **4.5.0-3**.
CAVA is optional. No installer command uses sudo or installs packages.

See [installation](docs/INSTALL.md) for the version gate and component dependencies.

## Quick start

Open a terminal in this repository:

```bash
./install.sh --dry-run
./install.sh
```

The first command previews and validates. The second installs only the visualizer;
it leaves the built-in bar operational. It adds a widget in `centerEnd`, beside the
clock, without moving existing widgets.

To opt into the island and launcher instead:

```bash
./install.sh --dry-run --components island,launcher,calendar,visualizer
./install.sh --components island,launcher,calendar,visualizer
```

**Prototype users:** existing unmanaged `stark.*` folders are never overwritten or
adopted. On the original development account these commands intentionally stop.
Use a clean test account/VM first. Your working prototype stays untouched.

## Updating and removing

```bash
./update.sh --dry-run
./update.sh
./uninstall.sh --dry-run
./uninstall.sh
```

Updates apply the current checkout; they do not silently fetch GitHub changes.
Removal restores only unchanged Stark-owned edits. Conflicts stop removal and keep
your files. Read [updating](docs/UPDATING.md) and [uninstalling](docs/UNINSTALL.md).

## Documentation

- [Install and select components](docs/INSTALL.md)
- [Configuration and themes](docs/CONFIGURATION.md)
- [Architecture and installation decisions](docs/ARCHITECTURE.md)
- [Updates and upstream compatibility](docs/UPDATING.md)
- [Removal and restoration](docs/UNINSTALL.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Validation evidence and limits](docs/VALIDATION.md)
- [Upstream attribution](docs/UPSTREAMS.md)
- [GitHub publishing](docs/PUBLISHING.md)

## Screenshots

No screenshot of the packaged release is claimed yet. The working prototype was
not reconfigured to produce release screenshots. Contributors should capture the
clean-account acceptance build and identify the version and components shown.

## License

Stark's original distribution/integration code is GPL-3.0-only; see [LICENSE](LICENSE).
Omarchy-derived portions retain MIT notices; Vyntaris adaptations retain GPL
attribution; System Monitor retains its MIT notice. Optional fonts are OFL-1.1.
See [third-party notices](THIRD_PARTY_NOTICES.md).
