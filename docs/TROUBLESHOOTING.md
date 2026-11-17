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
it available and automatically sets `bar.stark.fontFamily` when the island is selected.
Run `fc-match 'Shantell Sans'` to check discovery. Restart applications that cached
the old font list. No terminal font is changed.

## Failed transaction

Run `./install.sh --recover --dry-run`, review the reported journal, then use
`./install.sh --recover` if appropriate. Unexpected files are retained. Keep backups
until recovery is understood. See [UNINSTALL.md](UNINSTALL.md) for conflicts.

## Bootstrap refuses to install

Release mode requires a full reviewed commit SHA with `--commit`, matching the
selected `--ref` tag. A missing tag, failed clone, or mismatched SHA stops before
installer execution. No GitHub login is needed for this public repository.
`--dev-branch main` explicitly opts into unverified development. Do not bypass a
release mismatch; verify the release metadata independently.

## Wizard or selective removal

`--interactive` requires a real terminal. Use `--components` for automation.
Selective uninstall is rejected because current receipts have combined layout
changes; disable plugins natively or perform a reviewed full uninstall/reinstall.

## Installation finished but nothing looks different

- Minimal installs only the visualizer. It hides while locked, paused, or without a
  playing MPRIS player. Start media and check `omarchy-shell stark.visualizer status`.
- For the island use `./install.sh --mode standard --fonts --dry-run`, then install
  that profile after reviewing the plan. Fonts alone do not select the island.
- Previously managed disabled plugins stay disabled. `--reactivate` is explicit
  consent to enable them again. Other layout edits still trigger conflicts.
- `--no-reload` intentionally defers runtime activation. Restart the native shell
  manually after reviewing the files; do not launch a second Quickshell process.
- `omarchy plugin list` checks configured enabled state, not proof of rendering.
  Review Quickshell logs for failed QML imports/entry points.

## Missing dependencies

Run with `--install-deps` to review the precise package operation. Noninteractive
package permission requires `--install-deps --yes`. Refusing package installation
leaves desktop configuration unchanged. A failed pacman operation can still have
system-level effects; Stark does not remove packages on uninstall. Never use sudo
to run the entire installer or bypass a version/source mismatch.
