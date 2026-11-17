# Release audit — 2026-11-17

Plan, in priority order: preserve transactional architecture; harden source acquisition,
recovery and destination guards; add an optional wizard and argument validation;
expand isolated tests; reconcile installation and release documentation. No live
configuration changes or remote publishing are part of this audit.

## Confirmed defects and fixes

| Priority | Finding / cause | Disposition |
| --- | --- | --- |
| P0 | CAVA wrote a predictable runtime or /tmp path, allowing symlink clobbering | Private mktemp file, restrictive umask, cleanup traps |
| P1 | Bootstrap followed mutable main, merged into checkout even during preview | Temporary complete clone; release commit verification; explicit development option |
| P1 | Crash after file replacement but before journal observation left an unrecognized after-image | Persist intended hashes before writes/publication; recovery accepts before or intended image |
| P1 | Reads and state lock could follow symlink ancestors | Destination ancestor guards on reads and lock setup |
| P2 | Dry run did not parse shell.json or reject pending transactions | Added both preflight checks |
| P2 | Inapplicable CLI options silently ignored | Reject unsupported combinations, including selective uninstall |
| P2 | Dependency recursion had no cycle check | Actionable cycle error |
| P2 | System Monitor Text used automatic rich text for dynamic strings | Explicit plain text for owned Text elements |

## Retained strengths

Exact upstream/output hashes, dependency metadata, native manifest validation,
staged plugin copies, no elevated desktop installer, no keybinding replacement,
receipt ownership, semantic configuration reversal and conservative conflicts.
The island and its integration points remain intact.

## Remaining risks / improvements

- P1: No clean-account graphical acceptance cycle. Candidate only.
- P1: No independently published release SHA or verified bootstrap artifact yet.
  A SHA from the same untrusted download is not independent authentication.
- P1: SIGKILL during directory renames/native configuration mutation can require
  manual recovery. Before-images survive; unexpected content is retained.
- P2: Selective removal needs per-component activation provenance. Full conservative
  removal and native disable are supported; selective deletion is not implemented.
- P2: Configuration lists are atomic conflict units. Manual rearrangements require
  review before uninstall; no speculative layout reconstruction.
- P2: User-owned metadata is trusted; this does not defend against another process
  already running as the same user. No distributed lock against native editors.
- P2: Themes follow Omarchy; extra theme presets are not shipped. Wizard does not
  claim experimental panels are stable.
- P2: Version gates are intentionally narrow; later versions require source review.

Coverage: entry scripts, Python manager/helpers, tests/CI, manifests/locks,
configuration examples, documentation and plugin command/text sinks inspected.
No full external dependency source security audit or graphical certification claimed.

## Local integration follow-up

Confirmed causes of apparently invisible installation: default minimal mode does
not select the island; visualizer deliberately hides without playback; fonts were
only copied, not applied; prior disabled states were preserved without a prominent
explanation; no enabled-state postcondition was checked.

Added explicit minimal/standard/complete/custom modes, terminal default wizard,
permission-based mapped pacman prerequisites, root refusal, font detection/reuse,
cache refresh and exact-family verification, transactional font-setting application
and restoration, activation checks, explicit reactivation and clearer output.
Applying a new island font triggers a native shell restart even when plugin files
are unchanged. Existing security checks and prototype protection remain in place.

The current account has unmanaged prototype plugins and no managed receipt. A
real dry run of standard+fonts refused stark.bar without changing the desktop.
Read-only IPC outside the sandbox confirmed Omarchy shell availability and
Hyprland 0.56.2. No candidate plugins were activated; clean-account or explicitly
reviewed prototype migration approval is required before live acceptance.
