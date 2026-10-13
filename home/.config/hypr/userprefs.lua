-- █░█ █▀ █▀▀ █▀█   █▀█ █▀█ █▀▀ █▀▀ █▀
-- █▄█ ▄█ ██▄ █▀▄   █▀▀ █▀▄ ██▄ █▀░ ▄█

-- Set your personal hyprland configuration here
-- See https://wiki.hypr.land/Configuring for more information

-- Start Waybar through HyDE at login, using the selected theme and config.
hyde.config.start.bar = "hyde-shell waybar"

-- Pick a different random wallpaper from the active theme at each login.
-- Use the stable hyprpaper backend through the single HyDE startup handler.
hyde.config.start.wallpaper = "hyde-shell wallpaper --backend hyprpaper --random --global"

-- Normal Kitty terminals open tiled without taking over the workspace.
hl.window_rule({
    name = "user_kitty_tiled",
    match = { class = "^kitty$" },
    tile = true,
    fullscreen_state = "0 0",
    suppress_event = "maximize",
})

-- Brave localizes its picture-in-picture title in Spanish.
hl.window_rule({
    name = "user_brave_picture_in_picture",
    match = {
        class = "^brave-browser$",
        title = "^(Pantalla en pantalla|[Pp]icture[- ]?[Ii]n[- ]?[Pp]icture.*)$",
    },
    float = true,
    size = { 640, 360 }, -- Compact 16:9 video window.
    pin = true, -- Keep the video on its monitor across workspace changes.
})


-- // █ █▄░█ █▀█ █░█ ▀█▀
-- // █ █░▀█ █▀▀ █▄█ ░█░

-- 🔗 See https://wiki.hypr.land/Configuring/Variables/#input

-- =======================================================================
-- ROTACIÓN AUTOMÁTICA DE FONDO (Mismo Tema) - Optimizado para uwsm/NVIDIA
-- =======================================================================

-- Restore the window styling and special-workspace blur from the Hypr backup.
hl.config({
    general = {
        gaps_in = 3,
        gaps_out = 8,
        border_size = 2,
    },
    decoration = {
        rounding = 10,
        rounding_power = 2,
        dim_special = 0.3,
        active_opacity = 1.0,
        inactive_opacity = 1.0,
        shadow = {
            enabled = false,
        },
        blur = {
            enabled = true,
            size = 6,
            passes = 3,
            special = true,
            xray = false,
        },
    },
})

-- Apply the selected profile from My-dotfiles/hypr/animations/theme.conf.
-- The generated animations.lua only records the selection; it does not apply
-- the rules when the active entrypoint is Lua.
hl.curve("wind", { type = "bezier", points = { { 0.05, 0.9 }, { 0.1, 1.05 } } })
hl.curve("winIn", { type = "bezier", points = { { 0.1, 1.1 }, { 0.1, 1.1 } } })
hl.curve("winOut", { type = "bezier", points = { { 0.3, -0.3 }, { 0, 1 } } })
hl.curve("liner", { type = "bezier", points = { { 1, 1 }, { 1, 1 } } })
hl.curve("md3_decel", { type = "bezier", points = { { 0.05, 0.7 }, { 0.1, 1 } } })
hl.curve("menu_decel", { type = "bezier", points = { { 0.1, 1 }, { 0, 1 } } })
hl.curve("menu_accel", { type = "bezier", points = { { 0.38, 0.04 }, { 1, 0.07 } } })
hl.curve("easeInOutCirc", { type = "bezier", points = { { 0.85, 0 }, { 0.15, 1 } } })
hl.curve("OutBack", { type = "bezier", points = { { 0.34, 1.56 }, { 0.64, 1 } } })

hl.animation({ leaf = "windows", enabled = true, speed = 5, bezier = "easeInOutCirc" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 6, bezier = "winIn", style = "slide" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 5, bezier = "OutBack" })
hl.animation({ leaf = "windowsMove", enabled = true, speed = 5, bezier = "wind", style = "slide" })
hl.animation({ leaf = "border", enabled = true, speed = 1, bezier = "liner" })
hl.animation({ leaf = "borderangle", enabled = true, speed = 30, bezier = "liner", style = "loop" })
hl.animation({ leaf = "fade", enabled = true, speed = 3, bezier = "md3_decel" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 3, bezier = "menu_decel", style = "slide" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 1.6, bezier = "menu_accel" })
hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 2, bezier = "menu_decel" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 4.5, bezier = "menu_accel" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 7, bezier = "menu_decel", style = "slide" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 3, bezier = "md3_decel", style = "slidevert" })


-- Keep startup on the known-working fallback path. Wallpaper is handled by
-- HyDE's hyprpaper backend in variables.lua; tmp.sh only starts Waybar.
hl.dsp.exec_cmd("sleep 5 && ~/.config/hypr/scripts/cambio-cursor.sh")
hl.dsp.exec_cmd("firefox")

-- Keep the non-Super screenshot shortcut registered after all HyDE modules.
hl.bind("ALT + SHIFT + S", hl.dsp.exec_cmd("sh -c 'ARCHIVO=\"/tmp/Captura_$(date +%H-%M-%S).png\" ; grim -g \"$(slurp)\" \"$ARCHIVO\" && echo -n \"file://$ARCHIVO\"| wl-copy -t text/uri-list'"), { locked = true, description = "[Utilities|Screen Capture] recortar pantalla" })

-- 🔗 See https://wiki.hypr.land/Configuring/Variables/#gestures
-- hl.config.gestures = {
--     workspace_swipe = true,
--     workspace_swipe_fingers = 3
-- }

-- for window shallow similar to devour
-- hl.config.misc = {
--     enable_swallow = true,
--     swallow_regex = "(foot|kitty|allacritty|Alacritty|ghostty|Ghostty|org.wezfurlong.wezterm)"
-- }

-- Don't show update on first launch
-- hl.config.ecosystem = {
--     no_update_news = true
-- }
