# Installing Stark Shell

## Before starting

This release targets Omarchy Quattro **4.5.x**, Quickshell **0.3.2**, and Hyprland
**0.56.x**. It was built against Omarchy package **4.5.0-3**. These are deliberately
narrow bounds: a different Omarchy source file must be reviewed rather than patched
blindly. `omarchy version` is authoritative; an old packaged `version` text file
is not used as the detector.

Have `python3` (3.10 or later), `bash`, `jq`, `patch`, `omarchy`, `omarchy-shell`,
`quickshell`, and `hyprctl` available. Run inside your logged-in Omarchy session.
The installer reports missing commands and unsupported versions. With your
permission it installs missing prerequisites using `sudo pacman -S --needed`.
The rest of installation runs as your normal user. It never edits `/usr/share/omarchy`.

CAVA is optional. Without it, the visualizer uses a PipeWire peak-driven wave,
which is not a true spectrum. Install CAVA yourself if you want frequency analysis.
Fonts require `fc-cache` and `fc-match` from fontconfig when selecting `--fonts`.

## One local entry point

Open a terminal in the repository and run `./install.sh`. With no arguments in a
terminal it opens the wizard; without a terminal it retains minimal installation.
Do not run it with sudo. Python 3.10+ is required; if Python is missing, the Bash
entry point can offer its package installation before starting the Python manager.

```bash
./install.sh --interactive
./install.sh --mode standard --fonts --dry-run
./install.sh --mode standard --fonts --install-deps
```

The wizard and `--install-deps` show missing packages and ask permission before
running sudo. For explicit unattended approval use `--install-deps --yes`.
Only static mapped package names are passed to pacman: python, jq, patch,
quickshell, hyprland, and fontconfig as needed. Omarchy itself must already exist.
Version/source checks still run after packages are installed; installing a package
does not guarantee its current repository version is compatible with Stark.
The installer does not refresh package databases or perform a system upgrade.
If pacman fails, read its output and repair/update your Omarchy system separately.
Package changes are not part of Stark's desktop rollback or uninstall.

A dry run never invokes sudo or modifies configuration, fonts, plugins, cache,
backups or receipts. Missing prerequisites produce an incomplete preview and a
nonzero exit code. A full preview builds and validates in temporary storage.
A real install additionally requires the running Omarchy shell in your session.

There is no recommended remote one-line command yet. A release bootstrap needs a
reviewed script and an independently trusted release commit; development branches
are explicitly unverified. Use this local checkout while integration is tested.

## Modes

| Mode | Selection |
| --- | --- |
| minimal | Visualizer only; native bar remains |
| standard | Island, launcher, calendar, visualizer |
| complete | All components in the manifest lock (currently 14) |
| custom | Explicit `--components` list, plus dependencies |

Island/panel modes remain experimental, not certified stable. Fonts and animation
overrides are separate explicit options; `--fonts` installs/reuses and applies the
font automatically when the island is selected.

## Choose components

`--components` takes names separated by commas, with no spaces:

| Name | Plugin | Dependencies / behavior |
| --- | --- | --- |
| `visualizer` | `stark.visualizer` | Standalone; works with the native bar |
| `island` | `stark.bar` | Explicit full-bar replacement, retaining native widget architecture |
| `launcher` | `stark.menu` | Island; native menu with keyboard Apps list |
| `calendar` | `stark.clock` | Island; integrated calendar |
| `audio` | `stark.audio` | Island; native audio services |
| `network` | `stark.network` | Island; native network services |
| `bluetooth` | `stark.bluetooth` | Island; native Bluetooth services |
| `display` | `stark.monitor` | Island; native display panel |
| `battery` | `stark.power` | Island; native power/battery services |
| `weather` | `stark.weather` | Island; uses the device's existing weather configuration |
| `world-clock` | `stark.elsewhen` | Island; uses existing city settings |
| `agents` | `stark.agents` | Island; native agent integration |
| `wifiqr` | `stark.wifiqr` | Island; standalone Wi-Fi QR panel |
| `system-monitor` | `stark.system-monitor` | Island; optional third-party system dashboard |

Dependencies are added automatically and displayed during preview. Selecting any
integrated panel therefore opts into the island. Use `--mode complete` for all supported components, or name
what you want to install. Repeating installation adds components; it does not
silently remove previously selected ones. To reduce a profile, uninstall safely
and reinstall the desired selection.

```bash
./install.sh --components visualizer
./install.sh --components island,launcher,calendar,audio,visualizer
```

The first preserves the stock bar. The second explicitly selects the island.
Native clone activation preserves the source widget's position and per-widget
settings. New widgets use native placement rules; the visualizer is placed in
`centerEnd` so the clock is not shifted. Drag it into `center` if you want it
inside the island. No device-specific layout is shipped.

## Optional font and animations

```bash
./install.sh --components island,launcher --fonts --animations --dry-run
./install.sh --components island,launcher --fonts --animations
```

`--fonts` checks the exact family returned by fontconfig (a fallback font is not
accepted). If Shantell Sans is missing it copies the bundled, hash-verified font
files/license to your user font directory and refreshes that cache. An existing
font is reused and is never claimed or removed by this installer.

When the island is selected, it merges `bar.stark.fontFamily = "Shantell Sans"`
into shell.json, preserving other settings and recording the prior value in the
transaction backup/receipt. It verifies font availability before applying. A failed
verification rolls back. Font cache refresh still runs with `--no-reload`.
With minimal mode it makes the font available without changing the native font.
No terminal font or global fontconfig alias is changed. The existing island uses
shared Quickshell Style tokens, so other shell widgets may inherit its font while
that island is active.

`--animations` installs one Lua module and appends a marked `dofile` block to
`~/.config/hypr/hyprland.lua`. It enables horizontal workspace slides and an
accelerating downward window-close animation. It changes no keybindings.
Only regular Lua configuration files are supported; legacy `.conf` conversion and
symlink-managed configuration are not performed automatically.

`--no-reload` defers explicit restarts/reloads; use only for controlled staging.
Omarchy's existing file watchers can still observe saved files. Restart manually
before expecting the new QML to run.

## Where files go

- Plugins: `~/.config/omarchy/plugins/stark.*`, one complete managed copy per ID.
- Receipt/backups: `${XDG_STATE_HOME:-~/.local/state}/stark-shell/`.
- Optional fonts: `~/.local/share/fonts/stark-shell/`.
- Optional animation module: `~/.config/hypr/stark-shell-animations.lua`.

Omarchy's 4.5 plugin CLI assumes `~/.config`; a non-default `XDG_CONFIG_HOME` is
rejected. Moving `XDG_STATE_HOME` is supported, but retain the same setting for
updates and uninstall. Backups may contain private settings: keep state local,
not in GitHub or a shared dotfiles repository.

Existing unmanaged Stark folders are a conflict even if their contents happen to
match. This protects the prototype. There is no destructive `--force` or automatic
adoption option.

## Repeated installation and reactivation

Repeating installation/updates preserves disabled states and existing placements.
Use `./install.sh --reactivate` to explicitly enable managed components again.
Only a return to the receipt's exact enabled state is automatically reconciled;
other edited layouts remain conflicts. `--no-reload` leaves runtime verification
for you and prints a reminder. Visualizer visibility still depends on playback.
