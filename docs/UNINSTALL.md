# Safe removal

```bash
./uninstall.sh --dry-run
./uninstall.sh
```

The preview checks ownership and configuration conflicts without modifying files.
Removal deletes only receipt-owned files and reverses unchanged recorded edits.
It restores the previous selected bar and replaced native widget IDs/settings,
keeps unrelated plugins and personal configuration, and removes the exact optional
animation include while retaining unrelated Lua edits.

The receipt is stored under `${XDG_STATE_HOME:-~/.local/state}/stark-shell/state.json`.
Backups and transaction records remain in its `transactions` directory. They may
contain personal settings; do not publish them. Empty optional resource directories
may remain. The installer never removes unrelated contents just to tidy a directory.

## When removal reports a conflict

Nothing is removed if preflight finds an edited plugin, resource or managed JSON
path. This protects your work and avoids removing a plugin still referenced by the
configuration.

For an edited widget list, compare the receipt's `shell_changes` with your current
`shell.json`. Either restore that managed path to its recorded installed value
(after saving your edits), or remove the Stark IDs yourself while restoring any
native counterparts you want. Do not replace your whole configuration blindly.

After manually removing **all references to managed plugin IDs**, you may run:

```bash
./uninstall.sh --keep-config --dry-run
./uninstall.sh --keep-config
```

This retains your shell configuration as-is and still removes only unmodified
receipt-owned files. It refuses dangling references. Edited plugin/resource files
must still be resolved; `--keep-config` is not an overwrite bypass.

Deleting the receipt is not an uninstall method. Without it, files are unmanaged
and the installer intentionally refuses to claim or erase them.

## Fonts and system packages

The recorded island font setting is restored when unchanged. Fonts already present
before installation are reused and retained. Only hash-matching font files copied
by Stark are removed. Approved pacman dependencies are retained; they may be used
by other software and are outside the desktop transaction.
