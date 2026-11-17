# Stark Shell

A portable, reversible set of Omarchy Quattro plugins for Quickshell and Hyprland.
Stark builds on Omarchy's existing shell process, services, widgets, and shortcuts.
It does not install another desktop or launch a second shell.

**0.1.0 is a release candidate, pending graphical acceptance.** The default installation adds only the
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
CAVA is optional. Only explicitly approved missing prerequisite installation uses
`sudo pacman`; Stark itself always runs as your normal desktop user.

See [installation](docs/INSTALL.md) for the version gate and component dependencies.

## Local installation

Open a terminal in this repository and run:

```bash
./install.sh
```

With no arguments in a terminal, this opens a wizard. It offers Minimal,
Standard, Complete and Custom modes, Shantell Sans, and optional animations.
It shows the planned changes and asks before applying them. If packages are
missing, it explains the exact `sudo pacman` command and asks separately.
Never run `sudo ./install.sh`.

For the island, launcher, calendar, visualizer **and applied Shantell Sans**:

```bash
./install.sh --mode standard --fonts --install-deps
```

Preview the same selection first:

```bash
./install.sh --mode standard --fonts --dry-run
```

Standard explicitly replaces the bar with the existing expanding island while
preserving widget settings and shortcuts. Minimal adds just the visualizer to the
native bar; **the visualizer hides when media is paused or no player is detected**.
Complete installs all 14 supported components; island/panel profiles are still
experimental until graphical acceptance. Custom example:

```bash
./install.sh --mode custom --components island,launcher,calendar,visualizer --fonts
```

For automation, package installation needs explicit consent:

```bash
./install.sh --mode standard --fonts --install-deps --yes
```

Package additions are system changes and are not undone by Stark uninstall.
Dry runs never install packages. With missing prerequisites, the preview reports
an incomplete check and exits unsuccessfully until they are available.

**Prototype users:** unmanaged `stark.*` folders are never adopted or overwritten.
The original development account contains such folders; installation stops safely
there. Use a clean Omarchy account/VM, or first agree on a separate, reviewed
prototype migration. Removing folders blindly is not a migration.

There is no advertised remote one-line installation command yet. The bootstrap
retains commit verification and explicit development selection for release work,
but a published verified release is still required before recommending it.

## Verify what changed

```bash
omarchy plugin list
omarchy-shell shell ping
fc-match -f '%{family}\n' 'Shantell Sans'
omarchy-shell stark.visualizer status
```

The selected plugins should be enabled. Play media to see the visualizer; open the
launcher and calendar to test their island panels. The installer checks enabled
state before/after restart but cannot prove visual rendering. Normal updates keep
user-disabled plugins disabled; `./install.sh --reactivate` explicitly enables
managed components again, retaining conflict checks for other edits.

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

## Release status

Minimal is the conservative candidate profile. Island and integrated panels remain
experimental. See [audit](docs/AUDIT.md), [testing](docs/TESTING.md),
[development](docs/DEVELOPMENT.md), and [release checklist](docs/RELEASE.md).
Selective component removal and additional theme presets are planned. Use native
disable for temporary changes, or full conservative uninstall and reinstall.
