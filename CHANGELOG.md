# Changelog

## Unreleased local installation integration

- Add minimal, standard, complete and custom CLI modes; no-argument terminal wizard.
- Offer missing prerequisites with separate sudo pacman consent; reject running Stark as root.
- Detect/reuse or install Shantell Sans, refresh/verify it and transactionally apply the island font.
- Verify enabled components before/after restart; explain hidden visualizer and deferred reloads.
- Add explicit safe reactivation and preserve personally edited font settings.
- Expand isolated tests, including actual bundled-font resolution in a private Fontconfig cache.
- Keep prototype protection; live migration/installation requires owner approval.

## Unreleased candidate hardening

- Require a pinned release commit before bootstrap execution; explicit development mode.
- Use temporary checkouts, disable Git credential prompts, and propagate download failures.
- Journal intended hashes before mutations, guard symlink ancestors and validate previews.
- Add optional installation wizard, dependency-cycle errors and stricter CLI validation.
- Secure CAVA temporary files and render owned System Monitor text as plain text.
- Expand isolated regression coverage; document remaining release blockers.

## 0.1.0 — 2026-11-17

- Add one-line bootstrap installer (`curl ... | bash`) that clones a managed
  checkout into `~/.local/share/stark-shell` and runs the transactional installer,
  with dry-run preview, environment overrides and dirty-checkout refusal.
- Establish a version-controlled, user-scoped Stark Shell distribution.
- Default to the native Omarchy bar with a standalone media visualizer.
- Preserve the optional expanding island and 12 native/third-party panel integrations
  as pinned source references, small patches and original overlays.
- Preserve keyboard-driven island menu and list-based Apps without replacing
  the user's menu extension file or any default shortcuts.
- Add transactional install/update/uninstall, staging, native validation,
  backup journals, ownership hashes, conflict handling and interruption recovery.
- Add optional fonts and isolated Lua animation settings.
- Exclude the removed control center and defer dock redesign.
- Document the runtime acceptance work still required for the packaged release.
