# Installing Stark Shell

## Before starting

This release targets Omarchy Quattro **4.5.x**, Quickshell **0.3.2**, and Hyprland
**0.56.x**. It was built against Omarchy package **4.5.0-3**. These are deliberately
narrow bounds: a different Omarchy source file must be reviewed rather than patched
blindly. `omarchy version` is authoritative; an old packaged `version` text file
is not used as the detector.

Have `python3` (3.10 or later), `bash`, `jq`, `patch`, `omarchy`, `omarchy-shell`,
`quickshell`, and `hyprctl` available. Run inside your logged-in Omarchy session.
The installer reports missing commands and unsupported versions. It does not use
sudo, install packages, or edit `/usr/share/omarchy`.

CAVA is optional. Without it, the visualizer uses a PipeWire peak-driven wave,
which is not a true spectrum. Install CAVA yourself if you want frequency analysis.
Fonts require `fc-cache` only when selecting `--fonts`.

## Get the project

Download the repository, or clone its published GitHub URL with `git clone`. This
creates a working copy of the project; it does not change your desktop. Enter that
folder with `cd stark-shell` before running the following commands.

```bash
python3 tools/stark_manager.py doctor
./install.sh --dry-run
```

`doctor` prints detected versions. `--dry-run` builds in a temporary directory,
validates manifests, checks ownership conflicts and previews destinations. It does
not write desktop configuration, fonts, plugins, backups, or installation state.

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
integrated panel therefore opts into the island. There is no `all` shortcut: name
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

`--fonts` copies Shantell Sans and its license into your user font directory. It
does not change terminals or global font aliases. Selecting it for the island is
a separate documented setting.

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
