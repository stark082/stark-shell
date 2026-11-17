# Architecture

## One host process

Omarchy owns the long-lived Quickshell process. Stark supplies normal plugin
manifests and QML entry points; it never starts an additional shell. Service-backed
widgets continue using Omarchy's services and cloned host capabilities.

The first installation defaults to a standalone visualizer on the native bar.
The island is a deliberate optional replacement bar, not an installer assumption.
It is derived from the verified 4.5.0-3 native Bar and preserves native slot pools,
widget dragging, layout sections, tray, bar modes, and service API forwarding.

```text
Omarchy shell / services / default keybindings
  ├─ Native bar (default) ── Stark visualizer
  └─ Optional Stark bar
       ├─ Native modular widget/drag architecture
       ├─ BarShape + native theme tokens
       └─ NotchHost + per-monitor Bridge
            ├─ Launcher
            ├─ Calendar / weather / audio
            └─ Shared extra surface for independent panel integrations
```

The Bridge selects the focused monitor's top bar. A plugin keeps its native
controller/open state, reparents its content into the appropriate notch surface,
and hides the original popup while embedded. Non-top bars retain normal-popup
fallback. The host handles shared sizing, clipping, focus, Escape, and dismissal.
Calendar content stays measured at its final width to avoid resize jerking.

## Repository layout

- `overlays/`: original Stark files and adapted source files. These directories
  are **not complete installable plugins** by themselves.
- `patches/`: minimal unified diffs against installed Omarchy files.
- `packaging/upstreams.lock.json`: component dependencies, source hashes, output
  hashes, licenses and patch paths.
- `tools/stark_manager.py`: environment checks, build, install, update, ownership,
  transaction journals and uninstall.
- `hypr/`, `fonts/`: opt-in, isolated additions.
- `tests/`: temporary-home lifecycle tests and media matching regressions.
- `.build/`: ignored, complete materialized plugin directories for review/testing.

The removed control center is not a runtime dependency. The old dock clone and
LetsFG are not distributed as first-release requirements. Their original working
prototype folders are not changed. `packaging/prototype-inventory.json` records
prototype manifests and file hashes, not personal shell configuration or tokens.

## Why managed copies

The installed 4.5 CLI catalog uses `find -L` for root-level plugin directories,
which suggests root-directory symlinks can be discovered. But the validator
explicitly prohibits links inside plugins, and watcher/update behavior of a
linked monorepo root is not a documented installation guarantee. A link also
makes `git pull` mutate live QML before validation and conflict checks.

Stark therefore builds validated **managed copies** and publishes a complete
staged directory. Each plugin has one real root-level directory and a valid
manifest. During upgrade the previous directory is moved aside, then the new
complete directory is renamed into place. There is a brief name gap between those
renames; a final shell restart loads the validated version. There is never a
mixed set of old and new files. Before-images are saved before publication.

`omarchy plugin add` expects a plugin repository root; it is not used to pretend
that arbitrary subdirectories are independent Git packages. Users install this
monorepo with its installer. Native validation, discovery and activation commands
are used for each materialized plugin.

## Transactions and ownership

The package manager acquires a single-writer state lock. It builds/validates all
selected components before modifying desktop files, checks managed file hashes,
and refuses unmanaged collisions. It records before-images, file modes, expected
after hashes, component versions and environment versions in private state.

Plugin activation uses native CLI/IPC. The manager observes and validates the JSON
after each native operation and stores a semantic before/after diff. It does not
copy a template over `shell.json`. The shell's native mutator owns serialization.

Failure restores unchanged expected after-images. A concurrent edit makes rollback
retain that file and report a conflict. The journal survives an interrupted run;
`--recover` applies the same checks. SIGKILL can leave a partial transaction that
requires review; recovery never overwrites an unexpected file.

On uninstall, JSON objects are merged back by recorded paths. Lists are atomic:
manual reordering is a conflict. Unrelated keys survive. A marked animation
include can be removed while preserving edits elsewhere in the Lua file. Any
conflict stops uninstall before deleting plugin files.

Do not edit desktop settings concurrently with installation: the installer can
lock its own operations, not the graphical editor. It checks observed state before
native mutations, but it cannot attribute an edit made during an external native
command to its author. Backups and conflict checks reduce this narrow race; they
are not a distributed configuration lock.

## Candidate hardening

File writes journal both the observed image and intended replacement hash before
mutation, so recovery can recognize a crash before observation. Directory swap
and external native-command interruption windows still need conservative manual
review. Bootstrap checks an independently supplied release commit before running
installer code, uses temporary clones, and never updates the active source tree.

## Local setup and fonts

install.sh remains the single local entry point. It refuses root, can offer the
Python prerequisite when absent, and opens the wizard only for no-argument terminal
use. The Python manager handles named profiles, exact component dependencies and
consented package installation. Only static mapped prerequisite names are passed
to sudo pacman, with inherited terminal I/O. Packages are outside the desktop
transaction; no system package is removed on uninstall.

Fonts are exact-family checked through fontconfig. Existing Shantell Sans is
reused without ownership; otherwise verified bundled files are transactionally
installed and the cache refreshed. bar.stark.fontFamily is merged into shell.json
and included in its reversible semantic diff. A font-setting change restarts the
native shell unless reload is explicitly deferred. Native plugin enable remains
the activation mechanism; enabled state is checked before and after restart.
