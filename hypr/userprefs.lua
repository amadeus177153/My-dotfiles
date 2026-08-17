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


-- Arrancar el demonio de fondos en segundo plano
hl.dsp.exec_cmd("awww-daemon &")
hl.dsp.exec_cmd("hyde-shell waybar &")
hl.dsp.exec_cmd("sleep 2 && hyde-shell wallpaper -r")
hl.dsp.exec_cmd("sleep 5 && ~/.config/hypr/scripts/cambio-cursor.sh")
hl.dsp.exec_cmd("firefox")

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
