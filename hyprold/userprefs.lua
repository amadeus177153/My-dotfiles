-- █░█ █▀ █▀▀ █▀█   █▀█ █▀█ █▀▀ █▀▀ █▀
-- █▄█ ▄█ ██▄ █▀▄   █▀▀ █▀▄ ██▄ █▀░ ▄█

-- Set your personal hyprland configuration here
-- See https://wiki.hypr.land/Configuring for more information

-- // █ █▄░█ █▀█ █░█ ▀█▀
-- // █ █░▀█ █▀▀ █▄█ ░█░

-- 🔗 See https://wiki.hypr.land/Configuring/Variables/#input
hl.config.input = {
    -- kb_layout = "us",
    -- follow_mouse = 1,
    -- sensitivity = 0,
    -- force_no_accel = 0,
    -- accel_profile = "flat",
    -- numlock_by_default = true,

    touchpad = {
        natural_scroll = false
    }
}

-- =======================================================================
-- ROTACIÓN AUTOMÁTICA DE FONDO (Mismo Tema) - Optimizado para uwsm/NVIDIA
-- =======================================================================
hl.exec_once("sleep 3 && { swwwallpaper.sh -r || hyde wall random; }")
hl.exec_once("sleep 5 && ~/.config/hypr/scripts/cambio-cursor.sh")

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
