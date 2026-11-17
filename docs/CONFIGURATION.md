# Configuration

Stark keeps Omarchy's `~/.config/omarchy/shell.json`. It does not replace it with a
Stark template. Native plugin enable operations perform activation, preserve clone
settings/placement, and keep the existing tray, reminders and clipboard services.

## Rearrange widgets

Use Omarchy's bar editor or drag-and-drop. For example:

```bash
omarchy bar move stark.visualizer --section center
```

This moves the visualizer into the center group. With `stark.bar`, widgets in that
group are vertically centered within the full notch height. `centerBegin` and
`centerEnd` sit outside the notch's central box. The default installer puts the
visualizer in `centerEnd` to preserve the clock's center.

Use `omarchy plugin list` to see installed IDs and `omarchy plugin disable ID` to
disable a plugin. Clones use `omarchy.clonedFrom`, so native routing and source
restoration are preserved. Disabling an installed component is respected by
repeat installation and update unless you explicitly pass `--reactivate`.

## Island styling

The optional island reads `bar.stark` from your existing `shell.json`:

```json
{
  "bar": {
    "stark": {
      "fontFamily": "Shantell Sans",
      "minimumWidth": 186,
      "notchDepth": 11
    }
  }
}
```

This is a **fragment to merge**, not a replacement configuration. Keep all other
keys. `./install.sh --mode standard --fonts` automatically detects/installs the
font and merges the fontFamily setting, with a reversible backup. No manual font
application is needed. Omit fontFamily to follow Omarchy's normal font (manual
changes to managed values can require review during uninstall). Colors follow Omarchy's active palette
and shell theme tokens. There are no bundled monitor, network, weather or audio
identities.

The notch uses 180 ms entrance / 120 ms exit transitions through
`Style.duration`, respecting Omarchy's animations-off setting. A unified control
center is not present. Menu, calendar and other plugin panels retain independent
lifecycles and keyboard controls inside the host.

## Media visualization and focus

The visualizer runs CAVA only during MPRIS playback and while unlocked. It falls
back to the current PipeWire output's peaks if CAVA is absent. It displays five
bars from a 32-value stream. It does not start media playback or stream audio to
the network.

Clicking selects a uniquely matching media window and focuses its Hyprland
address. Dedicated web apps are supported by normalized track/window-title
matching. Browser tab selection is not implemented. If several windows match, it
avoids guessing; an app's supported MPRIS Raise method is the fallback.

```bash
omarchy-shell stark.visualizer status
omarchy-shell stark.visualizer target
```

These read-only diagnostics show playback/backend state and the selected app
class. `omarchy-shell stark.visualizer focus` invokes the same action as a click.

## Clipboard, reminders and shortcuts

All default Omarchy keybindings remain untouched. Stark uses the same shell, so
native clipboard and reminder integrations remain available through Omarchy's
normal commands and shortcuts. It does not claim to embed their full interfaces
inside the island. The native dock and its launcher shortcut are not replaced.

## Changes and uninstall conflicts

Unrelated changes to other JSON keys are preserved. Changing an array that Stark
modified (for example, moving a newly installed widget) is intentionally treated
as a conflict on uninstall; the installer will not reconstruct your preferred
layout by guessing. See [UNINSTALL.md](UNINSTALL.md).

## Optional network-backed panels

Selecting weather retains Omarchy's existing forecast provider and its local
location configuration, including its normal network refresh behavior. Other
native panels retain their upstream device/service behavior. The installer does
not export weather coordinates, city lists, audio devices or network identities
from the development account.

The optional System Monitor is read-only with respect to fan control in this
release. Its upstream privileged Asahi helper is disabled; Stark does not invoke
that helper automatically. Existing sysfs sensor readings remain available.

The island's existing Style binding can also affect widgets sharing Quickshell's
Style singleton while the island is active. Terminal settings and global fontconfig
aliases are untouched. Uninstall restores the recorded prior font setting when it
has not been edited and removes only font files installed by Stark itself.
