-- █░█ █▀ █▀▀ █▀█   █▀█ █▀█ █▀▀ █▀▀ █▀
-- █▄█ ▄█ ██▄ █▀▄   █▀▀ █▀▄ ██▄ █▀░ ▄█

-- Set your personal hyprland configuration here
-- See https://wiki.hypr.land/Configuring for more information

-- // █ █▄░█ █▀█ █░█ ▀█▀
-- // █ █░▀█ █▀▀ █▄█ ░█░

-- 🔗 See https://wiki.hypr.land/Configuring/Variables/#input

-- =======================================================================
-- ROTACIÓN AUTOMÁTICA DE FONDO (Mismo Tema) - Optimizado para uwsm/NVIDIA
-- =======================================================================

hl.on("hyprland.start", function()
    hl.dsp.exec_cmd("sleep 3 && { swwwallpaper.sh -r || hyde wall random; }")
end)
hl.on("hyprland.start", function()
    hl.dsp.exec_cmd("sleep 5 && ~/.config/hypr/scripts/cambio-cursor.sh")
end)

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
