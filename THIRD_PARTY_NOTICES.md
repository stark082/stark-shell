# Third-party notices

Stark Shell's original integration and packaging code is GPL-3.0-only.

- **Omarchy** — https://github.com/omacom/omarchy, package 4.5.0-3 / plugin versions
  recorded per component in `packaging/upstreams.lock.json`. MIT, Copyright David
  Heinemeier Hansson. See `licenses/Omarchy-MIT.txt`. Native source references and
  patches preserve the original code's MIT terms.
- **Vyntaris** — https://github.com/vyntaris/vyntaris, verified commit
  `967cdee5436b85e5a7ce8c6b300dddfddc820e03` for visualizer bars, service, shape, and slant
  helper. GPL-3.0; see `licenses/Vyntaris-GPL-3.0.txt` and the retained island
  `VYNTARIS-LICENSE`. Adaptations replace Vyntaris dependencies with Omarchy
  services/theme roles. Exact verified file hashes are in
  `packaging/vyntaris-provenance.json`. The wider downloaded archive's commit is
  not asserted merely from those matching files.
- **Omarchy System Monitor** — https://github.com/Harshith292002/omarchy-system-monitor,
  version 1.5.3. MIT, Copyright 2026 Harshith Chennupati. See
  `licenses/System-Monitor-MIT.txt`; local changes embed the panel in the island.
- **Shantell Sans** — https://github.com/google/fonts/tree/main/ofl/shantellsans,
  font version 1.011. SIL Open Font License 1.1, Copyright the Shantell Sans Project
  Authors. See `fonts/ShantellSans/OFL.txt`. Files are unmodified, opt-in assets;
  exact hashes are in `packaging/fonts.lock.json`.

These licenses are not replaced by the project's top-level license. Referenced
upstream source is obtained from the installed Omarchy package at build time,
not downloaded or executed as an unreviewed installer step.
