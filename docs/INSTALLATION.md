# Local installation

Run `./install.sh` in a terminal for the wizard. Preview the main components and font:

```bash
./install.sh --mode standard --fonts --dry-run
./install.sh --mode standard --fonts --install-deps
```

Standard selects the expanding island, launcher, calendar and visualizer. Shantell
Sans is detected/installed, verified and applied to the island in the same operation.
Missing dependencies require separate permission before sudo pacman is invoked.
Never run the whole installer as root.

See [the full guide](INSTALL.md) for modes, automation, optional animations,
compatibility, prototype conflicts and where backups are kept.
