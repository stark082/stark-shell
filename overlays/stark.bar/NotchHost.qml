import QtQuick
import qs.Commons
import "menu-bridge" as Integration

Item {
    id:host
    required property var bar
    property real stripHeight:26
    property real notchDepth:11
    property real closedWidth:186
    property bool opened:false
    property string page:""
    property string screenName:""
    property var embeddedMenu:null
    property var embeddedCalendar:null
    property bool calendarRevealed:false
    Timer {
        id:calendarReveal
        interval:Style.duration(80)
        onTriggered:host.calendarRevealed=host.opened && host.page==="calendar"
    }

    property var embeddedWeather:null
    property var embeddedAudio:null
    property var embeddedExtra:null
    property alias extraSurface:extraSurface
    function closeExtra(){if(embeddedExtra?.opened)embeddedExtra.close()}
    function openExtra(panel){
        if(embeddedExtra!==panel)closeExtra()
        if(embeddedAudio?.opened)embeddedAudio.close()
        if(embeddedWeather?.opened)embeddedWeather.close()
        if(embeddedCalendar?.opened)embeddedCalendar.close()
        if(embeddedMenu?.opened)embeddedMenu.close()
        embeddedExtra=panel;page="extra";opened=true
    }
    function extraClosed(panel){if(embeddedExtra===panel){embeddedExtra=null;if(page==="extra"){opened=false;page=""}}}

    property alias audioSurface:audioSurface
    property alias weatherSurface:weatherSurface
    property alias calendarSurface:calendarSurface
    property alias menuSurface:menuSurface
    Component.onCompleted:Integration.Bridge.registerHost(host)
    Component.onDestruction:Integration.Bridge.unregisterHost(host)
    function openMenu(menu){closeExtra();if(embeddedAudio?.opened)embeddedAudio.close();if(embeddedWeather?.opened)embeddedWeather.close();if(embeddedCalendar?.opened)embeddedCalendar.close();embeddedMenu=menu;page="menu";opened=true}
    function menuClosed(menu){if(embeddedMenu===menu){embeddedMenu=null;if(page==="menu"){opened=false;page=""}}}
    function openCalendar(calendar){
        if(embeddedCalendar===calendar && page==="calendar" && opened)return
        closeExtra()
        if(embeddedAudio?.opened)embeddedAudio.close()
        if(embeddedWeather?.opened)embeddedWeather.close()
        if(embeddedMenu?.opened)embeddedMenu.close()
        calendarRevealed=false
        embeddedCalendar=calendar;page="calendar";opened=true
        calendarReveal.restart()
    }
    function calendarClosed(calendar){if(embeddedCalendar===calendar){calendarReveal.stop();calendarRevealed=false;embeddedCalendar=null;if(page==="calendar"){opened=false;page=""}}}
    function openWeather(weather){closeExtra();if(embeddedAudio?.opened)embeddedAudio.close();if(embeddedMenu?.opened)embeddedMenu.close();if(embeddedCalendar?.opened)embeddedCalendar.close();embeddedWeather=weather;page="weather";opened=true}
    function weatherClosed(weather){if(embeddedWeather===weather){embeddedWeather=null;if(page==="weather"){opened=false;page=""}}}
    function openAudio(audio){closeExtra();if(embeddedMenu?.opened)embeddedMenu.close();if(embeddedCalendar?.opened)embeddedCalendar.close();if(embeddedWeather?.opened)embeddedWeather.close();embeddedAudio=audio;page="audio";opened=true}
    function audioClosed(audio){if(embeddedAudio===audio){embeddedAudio=null;if(page==="audio"){opened=false;page=""}}}




    property real panelWidth: opened ? (page==="extra" ? (embeddedExtra?.embeddedWidth ?? 380)+40 : page==="audio" ? (embeddedAudio?.embeddedWidth ?? 380)+40 : page==="weather" ? (embeddedWeather?.embeddedWidth ?? 480)+40 : page==="calendar" ? (embeddedCalendar?.embeddedWidth ?? 560)+40 : page==="menu" ? Math.max(380,(embeddedMenu?.cardWidth ?? 300)+40) : closedWidth) : closedWidth
    property real hang: opened ? Math.min((page==="extra"?(embeddedExtra?.embeddedHeight ?? 400)+16:page==="audio"?(embeddedAudio?.embeddedHeight ?? 400)+16:page==="weather"?(embeddedWeather?.embeddedHeight ?? 400)+16:page==="calendar"?(embeddedCalendar?.embeddedHeight ?? 400)+16:page==="menu"?(embeddedMenu?.cardHeight ?? 300)+16:notchDepth),height-stripHeight-24) : (bar.barHidden ? 0 : notchDepth)
    property real drawnWidth:panelWidth
    property real drawnHang:hang
    Behavior on drawnWidth { NumberAnimation { duration:Style.duration(host.opened?180:120);easing.type:Easing.OutCubic } }
    Behavior on drawnHang { NumberAnimation { duration:Style.duration(host.opened?180:120);easing.type:Easing.OutCubic } }
    property alias notchInput:hit
    function close(){closeExtra();if(embeddedAudio?.opened)embeddedAudio.close();if(embeddedWeather?.opened)embeddedWeather.close();if(embeddedCalendar?.opened)embeddedCalendar.close();if(embeddedMenu?.opened)embeddedMenu.close();opened=false;page=""}
    onOpenedChanged:{if(opened){forceActiveFocus();bar.requestPopout(host)}else{closeExtra();if(embeddedAudio?.opened)embeddedAudio.close();if(embeddedWeather?.opened)embeddedWeather.close();if(embeddedCalendar?.opened)embeddedCalendar.close();if(embeddedMenu?.opened)embeddedMenu.close();bar.releasePopout(host);page=""}}
    Keys.onEscapePressed: host.close()
    MouseArea { anchors.fill:parent;enabled:host.opened;onClicked:host.close() }
    Item {
        // With the bar disabled, draw only the island attached to the screen edge.
        x:(parent.width-width)/2
        width:host.bar.barHidden ? Math.min(parent.width,host.drawnWidth+88+host.drawnHang*0.1) : parent.width
        height:host.stripHeight+host.drawnHang+1
        clip:true
        BarShape {
            x:-parent.x;width:host.width;height:parent.height
            barHeight:host.stripHeight;corner:0
            backgroundColor:host.opened?host.bar.background:(host.bar.transparent?"transparent":host.bar.glassy?host.bar.glassBackground:host.bar.background)
            drawers:[{center:width/2,width:host.drawnWidth,hang:host.drawnHang}]
        }
    }
    Item {
        id:hit
        x:(parent.width-host.drawnWidth)/2-60;y:host.stripHeight
        width:host.drawnWidth+120;height:host.drawnHang
    }
    Item {
        id:menuSurface
        x:(parent.width-host.drawnWidth)/2+20;y:host.stripHeight+8
        width:host.drawnWidth-40;height:Math.max(0,host.drawnHang-16)
        visible:host.opened && host.page==="menu"
        clip:true
    }
    Item {
        id:calendarClip
        x:(parent.width-host.drawnWidth)/2+20;y:host.stripHeight+8
        width:Math.max(0,host.drawnWidth-40);height:Math.max(0,host.drawnHang-16)
        visible:host.opened && host.page==="calendar"
        clip:true
        Item {
            id:calendarSurface
            // Content stays centered at its final size; only the clip expands.
            x:(parent.width-width)/2
            width:host.embeddedCalendar?.embeddedWidth ?? 560
            height:Math.min(host.embeddedCalendar?.embeddedHeight ?? 400,host.height-host.stripHeight-40)
            opacity:host.calendarRevealed?1:0
            Behavior on opacity {NumberAnimation {duration:Style.duration(host.calendarRevealed?100:80);easing.type:Easing.OutCubic}}
        }
    }
    Item {
        id:weatherSurface
        x:(parent.width-host.drawnWidth)/2+20;y:host.stripHeight+8
        width:host.drawnWidth-40;height:Math.max(0,host.drawnHang-16)
        visible:host.opened && host.page==="weather"
        clip:true
    }
    Item {
        id:audioSurface
        x:(parent.width-host.drawnWidth)/2+20;y:host.stripHeight+8
        width:host.drawnWidth-40;height:Math.max(0,host.drawnHang-16)
        visible:host.opened && host.page==="audio"
        clip:true
    }
    Item {
        id:extraSurface
        x:(parent.width-host.drawnWidth)/2+20;y:host.stripHeight+8
        width:host.drawnWidth-40;height:Math.max(0,host.drawnHang-16)
        visible:host.opened && host.page==="extra"
        clip:true
    }
}
