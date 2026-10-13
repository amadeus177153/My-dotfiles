#!/bin/bash
if ! pgrep -x waybar >/dev/null 2>&1; then
    hyde-shell waybar > /dev/null 2>&1 & disown
fi
~/.config/hypr/scripts/cambio-cursor.sh > /dev/null 2>&1 & disown
