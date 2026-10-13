#!/usr/bin/env bash

# 1. Fuerza la ruta del usuario actual y busca la firma de Hyprland
export XDG_RUNTIME_DIR="/run/user/$(id -u)"

if [ -z "$HYPRLAND_INSTANCE_SIGNATURE" ]; then
    HYPR_DIR="$XDG_RUNTIME_DIR/hypr"
    if [ -d "$HYPR_DIR" ]; then
        export HYPRLAND_INSTANCE_SIGNATURE=$(ls -1 "$HYPR_DIR" | grep -v '^\.' | head -n 1)
    fi
fi

# 2. Lógica para iniciar o terminar la transmisión
if [ "$1" == "start" ]; then
    # APAGAR HDMI-A-1 primero
    hyprctl keyword monitor "HDMI-A-1, disable"
    # CAMBIAR RESOLUCIÓN de DP-1 a 1366x768@60Hz
    hyprctl keyword monitor "DP-1, 1366x768@59.79, 1920x0, 1"

elif [ "$1" == "stop" ]; then
    # VOLVER DP-1 a 1920x1080@240Hz
    hyprctl keyword monitor "DP-1, 1920x1080@240.30, 1920x0, 1"
    # REACTIVAR HDMI-A-1 (recargando configuración o encendiendo)
    hyprctl reload
    # Nota: Si por alguna razón 'hyprctl reload' no enciende tu HDMI-A-1 de vuelta, 
    # puedes reemplazar esa línea por la configuración nativa de tu monitor HDMI, ej:
    # hyprctl keyword monitor "HDMI-A-1, 1920x1080@60, 0x0, 1"
fi