pragma Singleton
import QtQuick
import Quickshell.Hyprland
QtObject {
    property var hosts:[]
    property var host:null
    property var menu:null
    function registerHost(item){if(hosts.indexOf(item)<0)hosts=hosts.concat([item]);if(!host)host=item}
    function unregisterHost(item){hosts=hosts.filter(h=>h!==item);if(host===item)host=hosts[0] ?? null}
    function selectHost(){
        const name=Hyprland.focusedMonitor?.name ?? "";
        host=hosts.find(h=>h.screenName===name && h.bar.position==="top") ?? hosts.find(h=>h.bar.position==="top") ?? null;
        return host;
    }
}
