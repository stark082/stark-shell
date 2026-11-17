pragma Singleton
import Quickshell
import Quickshell.Io
import Quickshell.Services.Pipewire
import QtQuick
import Quickshell.Services.Mpris

Singleton {
    id: root

    property bool locked: false
    readonly property var players: Mpris.players.values
    readonly property var activePlayer: players.find(p => p.isPlaying) ?? players[0] ?? null
    readonly property int count: 32
    readonly property bool wanted: (activePlayer?.isPlaying ?? false) && !locked
    property bool cavaMissing: false
    readonly property bool usingCava: wanted && !cavaMissing
    property var bars: []

    // Adapted from Vyntaris: native MPRIS and Omarchy lock state.
    onWantedChanged: if (!wanted) bars = []

    Process {
        id: cava
        running: root.usingCava
        command: ["sh", "-c",
            "command -v cava >/dev/null || exit 127; umask 077; f=$(mktemp \"${XDG_RUNTIME_DIR:-/tmp}/stark-shell-cava.XXXXXXXX\") || exit 1; trap 'rm -f -- \"$f\"' EXIT; trap 'exit 143' TERM; trap 'exit 130' INT; "
            + `printf '%s\\n' '[general]' 'bars = ${root.count}' 'framerate = 40' 'sensitivity = 90' `
            + `'[output]' 'method = raw' 'raw_target = /dev/stdout' 'data_format = ascii' 'ascii_max_range = 100' `
            + `'bar_delimiter = 59' 'frame_delimiter = 10' '[smoothing]' 'noise_reduction = 70' > "$f"; cava -p "$f"`]
        stdout: SplitParser {
            onRead: line => root.bars = line.split(";").filter(s => s !== "").map(v => Math.min(1, Number(v) / 100))
        }
        onExited: code => { if (root.wanted && code !== 0) root.cavaMissing = true; }
    }

    PwNodePeakMonitor {
        id: peaks
        node: Pipewire.defaultAudioSink
        enabled: root.wanted && root.cavaMissing
    }
    property real phase: 0
    Timer {
        interval: 33
        repeat: true
        running: root.wanted && root.cavaMissing
        onTriggered: {
            root.phase += 0.23;
            const p = Math.min(1, peaks.peak * 1.6);
            const out = [];
            for (let i = 0; i < root.count; i++) {
                const wave = 0.5 + 0.5 * Math.sin(root.phase + i * 0.55) * Math.cos(root.phase * 0.37 + i * 0.21);
                const prev = root.bars[i] ?? 0;
                out.push(prev * 0.55 + p * (0.25 + 0.75 * wave) * 0.45);
            }
            root.bars = out;
        }
    }

    function group(n) {
        if (bars.length === 0) return Array(n).fill(0);
        const out = [], size = Math.max(1, Math.floor(bars.length / n));
        for (let i = 0; i < n; i++) {
            let sum = 0;
            for (let k = 0; k < size; k++) sum += bars[Math.min(bars.length - 1, i * size + k)];
            out.push(sum / size);
        }
        return out;
    }
}
