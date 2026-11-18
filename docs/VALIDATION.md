# Validation evidence

Recorded on 2026-11-17. These results distinguish static/package checks from
actual graphical runtime acceptance.

## Completed

| Check | Result |
| --- | --- |
| Isolated lifecycle tests | 33 passed, using temporary HOME/config/state and mocked native commands |
| Media focus regressions | 6 cases passed using Node.js |
| Bash syntax | install, update, uninstall and test runner passed |
| ShellCheck | 0.11.0, entry/test scripts and the bundled sensor-discovery helper passed |
| Lua syntax | Optional animation module passed `luac -p` |
| JSON/package consistency | 19 JSON documents, 14 blueprints, source/output references and font hashes checked |
| Native Omarchy validator | All 14 complete materialized plugins passed `omarchy plugin validate` |
| QML syntax | Qt's `qmlformat` parser accepted all 53 materialized QML files, without editing them |
| Real environment detection | Omarchy 4.5.0-3; Quickshell 0.3.2, revision 2b4501a282689792b62e94f3fb30d8f512324fe6; Hyprland 0.56.2 |
| Existing prototype protection | Real-account dry run refused the unmanaged `stark.visualizer` folder, as intended |
| Prototype preservation | All recorded prototype file hashes were unchanged after development |
| Vyntaris provenance | Original visualizer, bars, shape and slant files matched the recorded upstream commit |

Lifecycle tests cover fresh/repeated/selective install, missing optional CAVA,
unsupported versions/interfaces, existing configuration preservation, unmanaged
collisions, upgrades/removal of obsolete owned files, activation/reload failures,
rollback/recovery, safe uninstall, manual file/list/include conflicts, symlinks,
font integrity, absent initial config, original configuration modes, and invalid initial JSON rejection.

ShellCheck was run from a temporary downloaded official release, not installed as
a system package. Tests invoke mock Omarchy/Hyprland/font-cache commands; they do
not restart the development desktop. Build/manifest/QML checks read the real
installed Omarchy sources but do not activate the generated plugins.

## Not yet verified for this packaged release

- A real fresh-account installation, reboot, upgrade and uninstall cycle.
- Graphical keyboard navigation, focus, popout switching, drag/rearrangement,
  transparency modes and service-backed widgets under the packaged island.
- Multiple monitors, mixed scaling, panel placement on non-top bars, or ARM hardware.
- Runtime CAVA failure/recovery, lock/unlock, multiple simultaneous MPRIS players,
  and title matching across browser profiles/languages in a clean account.
- Font rendering/fallback on devices without the prototype's Nerd Font setup.
- Automatic compatibility with later Omarchy, Quickshell or Hyprland releases.

The historical prototype was exercised interactively during development; that is
not substituted for a clean-account test of this packaging. QML parsing and native
manifest validation do not prove service behavior or graphical runtime correctness.

## Clean-account acceptance checklist

1. Snapshot a disposable Omarchy 4.5.0-3 VM or use a separate test account.
2. Verify default keybindings and baseline clipboard/reminders before installation.
3. Preview and install only `visualizer`; confirm the native bar, tray, service
   widgets and existing layout/settings remain operational.
4. Test CAVA, fallback without CAVA, pause/resume and lock/unlock.
5. Install `island,launcher,calendar,audio,network,bluetooth,display,battery`.
6. Exercise keyboard navigation, Escape, click-outside dismissal, panel switching,
   dragging widgets, all bar background modes and both native/custom service widgets.
7. Test mixed monitor scaling and move the bar away from the top to check fallback.
8. Change unrelated configuration; update twice and confirm no duplicate entries.
9. Introduce a managed-file edit and verify conflict retention; resolve it.
10. Preview/uninstall and verify restoration of the prior bar, layout and shortcuts.
11. Record versions, logs and release screenshots before promoting the island default.

## Targeted follow-up — 2026-11-18

With `bar-off` enabled, the live prototype's menu was summoned into a temporary
top-center island. The bar widgets remained hidden; closing the menu reduced the
island's target depth to zero and preserved the hidden-bar flag. The corresponding
packaged island and launcher rebuilt and passed native validation and QML parsing.
This targeted check does not replace the full clean-account release acceptance
matrix above.
