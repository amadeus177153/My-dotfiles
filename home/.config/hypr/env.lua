-- ~/.config/hypr/env.lua
-- Forzar variables de entorno para aplicaciones de KDE/Dolphin

hl.config({
    env = {
        -- Esto es vital para que Dolphin encuentre los archivos .desktop
        "XDG_MENU_PREFIX,arch-",
        "XDG_CURRENT_DESKTOP,KDE",
        "QT_QPA_PLATFORMTHEME,qt6ct",
    },
})

-- Ejecutar la reconstrucción de la base de datos al inicio de la sesión
hl.dsp.exec_cmd("kbuildsycoca6 --noincremental")