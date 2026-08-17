#!/bin/bash
awww-daemon > /dev/null 2>&1 & disown
hyde-shell waybar > /dev/null 2>&1 & disown
hyde-shell wallpaper -r > /dev/null 2>&1 & disown
~/.config/hypr/scripts/cambio-cursor.sh > /dev/null 2>&1 & disown
