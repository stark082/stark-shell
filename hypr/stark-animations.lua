-- Optional Stark motion overrides. No bindings are changed.
hl.animation({ leaf = "workspaces", enabled = true, speed = 3, bezier = "easeOutQuint", style = "slide" })
hl.curve("starkCloseAccelerate", { type = "bezier", points = { { 0.3, 0 }, { 0.8, 0.15 } } })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 2.2, bezier = "starkCloseAccelerate", style = "slide bottom" })
