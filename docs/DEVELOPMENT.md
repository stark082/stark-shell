# Development

See [contributing](CONTRIBUTING.md) for rebuilding pinned plugins and refreshing
patches. The existing architecture stays overlays + exact upstream patches +
transactional manager; do not copy full desktop defaults over user settings.

Run the checks in [TESTING.md](TESTING.md). Make focused changes and update output
hashes for changed overlays. Keep source pins unchanged unless porting upstream.
Use a disposable account/VM for activation, never the working prototype.
