# Updating

Updates apply the current local checkout. They do not fetch code automatically.
Review the changelog and upstream pins before installing a new release.

```bash
git status
git pull --ff-only
./update.sh --dry-run
./update.sh
```

`git status` shows local edits. `git pull --ff-only` accepts only a straightforward
upstream update, refusing to invent a merge. The dry run checks dependencies,
source compatibility and installed-file ownership. The final command updates
managed files while leaving existing widget placement and enabled/disabled
choices unchanged. Previously selected font/animation options stay selected.

A modified installed plugin is a conflict. Keep a copy of your changes, port them
into a development branch, and review them before updating. There is no `--force`
that discards local work. Edit source in the repository, update the relevant patch
record, rebuild and test rather than editing deployed files for routine work.

## Omarchy updates

Supported environment family: Omarchy 4.5.x, Quickshell 0.3.2, Hyprland 0.56.x.
Integrated clones were reconstructed from Omarchy package 4.5.0-3. Exact hashes
protect referenced upstream files. A newer 4.5 package may therefore still be
refused for a component whose source changed. The standalone visualizer has no
native source patch, but still checks required shell interfaces and version bounds.

When a pin fails:

1. Keep the installed working version. Do not edit packaged Omarchy sources.
2. Compare the changed native API/file with `packaging/upstreams.lock.json`.
3. Port the small patch, paying special attention to service-backed APIs,
   `omarchy.clonedFrom`, menu/IPC routing, slot geometry and popup focus.
4. Update pins and attribution in a branch; rerun all tests and the clean-account
   acceptance matrix before widening compatibility.

Native Omarchy files are never modified, so disabling/removing a clone can restore
its upstream implementation. Full copies are generated at build time; unchanged
upstream source is not duplicated throughout this repository.

## Recovery

```bash
./install.sh --recover --dry-run
./install.sh --recover
```

The first lists unfinished transactions. The second restores only files matching
the transaction's expected state, retaining conflicts. Review the reported backup
folder and restart the shell manually after a recovery. Journals and backups are
retained for investigation, not silently deleted.
