# Troubleshooting

## Unsupported version or source hash

Run `python3 tools/stark_manager.py doctor`. The first release is intentionally
narrowly pinned. A hash mismatch means the installed upstream file differs; see
[UPDATING.md](UPDATING.md). Do not force an old patch onto new shell APIs.

## Existing unmanaged plugin

Your original `stark.*` prototype is not owned by this installer. It is preserved.
Use a clean account/VM for the packaged release. If migrating manually, back up the
prototype and configuration first, disable/relocate only the selected prototype
folders, and review a dry run. Automatic prototype adoption is not implemented.

## Omarchy is not responding

Run `omarchy-shell shell ping` inside the logged-in desktop session. Review the
shell logs with `quickshell log -p /usr/share/omarchy/shell -t 50 --no-color`.
This displays recent shell diagnostics; it does not reset configuration. If needed,
run `omarchy restart shell`. Do not run a factory refresh to repair a package error.

## Animation override errors

Run `hyprctl configerrors` to read errors and `hyprctl reload` after correcting
user configuration. The optional module requires the supported Lua configuration.
It does not convert legacy Hyprland `.conf` files or modify any keybindings.

## Visualizer missing

It appears only while an MPRIS player reports playback and the screen is unlocked.
Use `omarchy-shell stark.visualizer status`. CAVA is optional; when absent,
PipeWire peaks drive the fallback wave. Silent output can show only minimal bars.
No microphone capture or external telemetry is added by this component.

## A click does not find the player

Use `omarchy-shell stark.visualizer target`. An app must expose MPRIS metadata and
have a uniquely matching window. A dedicated YouTube Music/YouTube web app is more
reliable than a background browser tab. Titles may be shortened or localized;
ambiguous cases deliberately avoid focusing an unrelated window. No browser
extension, remote-debugging port or automatic tab manipulation is installed.

## Font is not in Omarchy's font picker

That picker lists monospace fonts. Shantell Sans is proportional. `--fonts` makes
it available to applications; set `bar.stark.fontFamily` separately for the island.
Run `fc-match 'Shantell Sans'` to check discovery. Restart applications that cached
the old font list. No terminal font is changed.

## Failed transaction

Run `./install.sh --recover --dry-run`, review the reported journal, then use
`./install.sh --recover` if appropriate. Unexpected files are retained. Keep backups
until recovery is understood. See [UNINSTALL.md](UNINSTALL.md) for conflicts.
