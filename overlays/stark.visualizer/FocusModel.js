// Match existing player windows without falling back to an unrelated browser.
function normalize(value) {
  return String(value || "").normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
    .toLowerCase().replace(/\s*[-|—–]\s*(youtube|youtube music|spotify|brave|google chrome|mozilla firefox)(\s*[-|].*)?$/i, "")
    .replace(/[^a-z0-9\u0080-\uffff]+/g, " ").trim()
}
function appKey(value) {
  return String(value || "").toLowerCase().replace(/\.desktop$/, "").replace(/-browser$/, "")
}
function isBrowser(player) {
  return /brave|chromium|chrome|firefox|vivaldi|edge|opera|helium/.test(appKey(player.identity)+" "+appKey(player.desktopEntry))
}
function candidates(player, windows) {
  var browser = isBrowser(player)
  var keys = [appKey(player.desktopEntry),appKey(player.identity)].filter(key => key.length > 0)
  return windows.filter(window => {
    var id = appKey(window.appId)
    var webApp = /^(chrome|brave|chromium|vivaldi|msedge)-/.test(id)
    return id && ((browser && webApp) || keys.some(key => id === key || id.split(".").pop() === key.split(".").pop()))
  })
}
function titleScore(track, windowTitle) {
  var a=normalize(track), b=normalize(windowTitle)
  if (!a || !b) return 0
  if (a===b) return 100
  if (Math.min(a.length,b.length)>=8 && (a.includes(b) || b.includes(a))) return 90
  var x=Array.from(new Set(a.split(" ").filter(t=>t.length>1)))
  var y=Array.from(new Set(b.split(" ").filter(t=>t.length>1)))
  var shared=x.filter(t=>y.includes(t)).length
  return shared>=3 && shared/Math.min(x.length,y.length)>=0.8 ? 60 : 0
}
function choose(player, windows) {
  var items=candidates(player,windows)
  var scored=items.map(window=>({window:window,score:titleScore(player.trackTitle,window.title)})).filter(item=>item.score>0)
  scored.sort((a,b)=>b.score-a.score)
  if (scored.length && (scored.length===1 || scored[0].score>scored[1].score)) return scored[0].window
  if (!isBrowser(player) && items.length===1) return items[0]
  return null
}
if (typeof module !== "undefined") module.exports={normalize,candidates,titleScore,choose}
