# Upstream tracking

`packaging/upstreams.lock.json` is the machine-readable source of truth. For each
component it records repository, release/plugin version (or verified commit),
license, modified files, purpose, dependencies, compatibility constraints and
per-file source/output SHA256 hashes.

The Omarchy baseline is package **4.5.0-3**. Native plugins advertise their own
versions independently of that package. Both are recorded. Source hashes are
checked before applying patches with `--fuzz=0`; the final output hash is checked
again afterward. A changed upstream is a compatibility conflict, not permission
to apply a fuzzy patch.

| Component | Upstream | Changes |
| --- | --- | --- |
| Island | Omarchy Bar + Vyntaris geometry | Shared notch host, shape, centering, configurable styling |
| Launcher | Omarchy menu | Island content host; keyboard Apps list; user extensions merge last |
| Calendar | Omarchy clock | Island calendar embedding and stable reveal sizing |
| Audio | Omarchy audio | Native panel embedding |
| Network | Omarchy network | Native panel embedding |
| Bluetooth | Omarchy Bluetooth | Native panel embedding |
| Display | Omarchy monitor | Native panel embedding |
| Battery | Omarchy power | Native panel embedding |
| Weather | Omarchy weather | Native panel embedding; device location stays local |
| World clock | Omarchy elsewhen | Native panel embedding; user cities stay local |
| Agents | Omarchy agents | Native panel embedding |
| Wi-Fi QR | Omarchy wifiqr | Native panel embedding |
| System Monitor | Harshith 1.5.3 | Native dashboard embedding |
| Visualizer | Vyntaris commit in provenance file | Omarchy theme/lock services, CAVA fallback, media-window focus |

Vyntaris visualizer, Bars, BarShape and Slant helper source were compared byte-for-byte to
commit `967cdee5436b85e5a7ce8c6b300dddfddc820e03`. `BarShape.qml` includes later local
prototype modifications; its output is pinned separately. A snapshot of prototype
manifests and file hashes records the starting point without exporting shell.json,
credentials or device settings.

To port an upstream update, compare its source with the pinned version, review the
API changes, regenerate the minimal patch, and run the full static plus runtime
acceptance matrix. Do not invent a source commit for an unversioned archive.

The System Monitor adaptation additionally disables privileged Asahi fan-control
invocation for the portable first release. Sensor display remains read-only; no
fan-control daemon, sudo policy or system-wide helper is installed.
