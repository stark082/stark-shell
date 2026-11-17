# Candidate release checklist

Use semantic versioning: breaking CLI/state changes require a documented migration;
fixes use patch versions. Keep VERSION, lock release and plugin versions consistent.
Existing schema-1 receipts remain compatible with this candidate. Downgrades are
not certified; retain the prior source and transaction backups.

1. Run CI, package checks, lifecycle and bootstrap regressions.
2. Complete fresh-account graphical install/update/reboot/uninstall acceptance.
3. Review audit blockers, licenses, source pins and release diff.
4. Record exact tested environment, known issues and upgrade instructions.
5. After maintainer authorization, tag the reviewed commit and publish notes.
6. Publish the full commit SHA through an independently trusted channel; provide
   a verified bootstrap artifact/checksum or signature with documented trust setup.
7. Test the published tag installation command and failure paths in a clean VM.

No release/tag/push is performed by this checklist. Until these steps pass, call
this a candidate. Never recommend an unchecked curl pipe as verified installation.

Candidate notes: safer source acquisition, private CAVA temporary files, write-ahead
recovery hashes, symlink guards, terminal wizard and expanded tests. Island panels
remain experimental. Selective removal, additional theme presets and complete
SIGKILL recovery of directory swaps remain known limitations; see AUDIT.md.
