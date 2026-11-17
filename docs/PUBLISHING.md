# Publishing on GitHub

The repository is prepared locally. It is not automatically published, and no
remote account or repository is created by the installer.

1. Review `git status` and `git log -1`. Ensure no credentials, personal config,
   state receipts, backups or private screenshots are staged.
2. Run the tests and review `docs/VALIDATION.md`. Keep unverified runtime behavior
   explicit in the release notes.
3. Create an empty GitHub repository named `stark-shell` in your account. Do not
   initialize a second README/license there.
4. Connect and push your local repository:

```bash
git remote add origin https://github.com/YOUR-ACCOUNT/stark-shell.git
git push -u origin main
```

Replace `YOUR-ACCOUNT` with your GitHub username. The first command records where
to publish; the second uploads the commits. Authentication is handled by Git/GitHub.

After a reviewed release, create and push a version tag:

```bash
git tag -a v0.1.0 -m 'Stark Shell 0.1.0'
git push origin v0.1.0
```

A tag names the exact source revision. Add GitHub release notes explaining the
supported versions, optional island status, validation evidence and limitations.
Do not claim marketplace `omarchy plugin add` support for this whole monorepo.
Independent plugin publishing would need separate complete plugin repositories
or generated release artifacts with clear dependency handling.
