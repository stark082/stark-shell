import QtQuick
import Quickshell.Io
import Quickshell.Wayland
import Quickshell.Hyprland
import qs.Ui
import qs.Commons
import "."
import "FocusModel.js" as FocusModel

BarWidget {
  id: root
  moduleName: "stark.visualizer"
  readonly property var lockService: bar?.shell?.firstPartyServiceFor("omarchy.lock") ?? null
  Binding { target: Visualizer; property: "locked"; value: root.lockService?.locked ?? false }
  visible: Visualizer.wanted
  implicitWidth: visible ? 30 : 0
  implicitHeight: barSize
  Bars {
    anchors.centerIn: parent
    width: 22; height: 14
    count: 5; gap: 2.5; minimum: 0.18
    values: Visualizer.group(5)
  }
  property string lastFocusResult: ""
  function playerWindows() {
    var player = Visualizer.activePlayer
    return player ? FocusModel.candidates(player, ToplevelManager.toplevels.values) : []
  }
  function focusPlayer() {
    var player = Visualizer.activePlayer
    if (!player) return root.lastFocusResult = "no-player"
    var target = FocusModel.choose(player, ToplevelManager.toplevels.values)
    if (target) {
      var window = Hyprland.toplevels.values.find(item => item.wayland === target)
      var address = String(window?.address || "")
      if (address && !address.startsWith("0x")) address = "0x" + address
      if (/^0x[0-9a-f]+$/i.test(address)) {
        Hyprland.dispatch('hl.dsp.focus({window = hl.get_window("address:' + address + '")})')
        return root.lastFocusResult = "focused"
      }
      target.activate()
      return root.lastFocusResult = "activation-requested"
    }
    if (player.canRaise) {
      player.raise()
      return root.lastFocusResult = "raise-requested"
    }
    return root.lastFocusResult = "no-unique-media-window"
  }
  MouseArea {
    anchors.fill: parent
    cursorShape: Qt.PointingHandCursor
    onClicked: root.focusPlayer()
  }
  ShellIpc {
    target: "stark.visualizer"
    function focus(): string { return root.focusPlayer() }
    function target(): string { return JSON.stringify({lastFocusResult:root.lastFocusResult,selectedWindow:Visualizer.activePlayer ? (FocusModel.choose(Visualizer.activePlayer,ToplevelManager.toplevels.values)?.appId ?? "") : "",player:Visualizer.activePlayer?.identity ?? "",desktopEntry:Visualizer.activePlayer?.desktopEntry ?? "",canRaise:Visualizer.activePlayer?.canRaise ?? false,matchingWindows:root.playerWindows().length}) }
    function status(): string { return JSON.stringify({playing:Visualizer.wanted,usingCava:Visualizer.usingCava,fallback:Visualizer.cavaMissing,bars:Visualizer.bars.length,locked:Visualizer.locked}) }
  }
}
