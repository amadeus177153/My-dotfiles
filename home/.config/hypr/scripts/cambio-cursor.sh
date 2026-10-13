#!/bin/bash

# Apply the cursor belonging to the currently selected HyDE theme.
state_file="$HOME/.local/state/hyde/staterc"
theme_name=""
if [[ -r "$state_file" ]]; then
    theme_name=$(sed -n 's/^HYDE_THEME="\(.*\)"$/\1/p' "$state_file")
fi

theme_file="$HOME/.config/hyde/themes/$theme_name/hypr.theme"
[[ -r "$theme_file" ]] || exit 0

cursor_theme=$(sed -n 's/^[[:space:]]*\$CURSOR_THEME[[:space:]]*=[[:space:]]*//p' "$theme_file" | head -n1 | tr -d '[:space:]\"')
cursor_size=$(sed -n 's/^[[:space:]]*\$CURSOR_SIZE[[:space:]]*=[[:space:]]*//p' "$theme_file" | head -n1 | tr -d '[:space:]\"')

[[ -n "$cursor_theme" && "$cursor_size" =~ ^[0-9]+$ ]] || exit 0
hyprctl setcursor "$cursor_theme" "$cursor_size"
