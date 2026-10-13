#!/usr/bin/env bash
set -euo pipefail

save_dir="$HOME/Imágenes/Screenshots"
mkdir -p "$save_dir"
file="$save_dir/Captura_$(date +%H-%M-%S).png"

move_cursor() {
  hyprctl dispatch "hl.dsp.cursor.move({ x = $1, y = $2 })" >/dev/null
}

# Give slurp the visible window rectangles so it can select a window or a free area.
fullscreen_workspaces=$(hyprctl workspaces -j | jq -c 'map(select(.hasfullscreen) | .id)')
visible_workspaces=$(hyprctl monitors -j | jq -c '[.[] | if .specialWorkspace.name == "" then .activeWorkspace.id else .specialWorkspace.id end]')
window_geometries=$(hyprctl clients -j | jq -r --argjson visible "$visible_workspaces" --argjson fullscreen "$fullscreen_workspaces" '
  .[] | select((.workspace.id | IN($visible[])) and ((.workspace.id | IN($fullscreen[])) | not) or .fullscreen > 0)
  | "\(.at[0]),\(.at[1]) \(.size[0])x\(.size[1])"
')
geometry=$(printf '%s\n' "$window_geometries" | slurp) || exit 0

# When a window is selected, move the pointer outside its bounds for the
# capture, then put it back. This also avoids cursor images some compositor
# paths include even when grim's cursor option is omitted.
if grep -Fxq -- "$geometry" <<< "$window_geometries" && [[ "$geometry" =~ ^(-?[0-9]+),(-?[0-9]+)[[:space:]]+([0-9]+)x([0-9]+)$ ]]; then
  gx=${BASH_REMATCH[1]}; gy=${BASH_REMATCH[2]}; gw=${BASH_REMATCH[3]}; gh=${BASH_REMATCH[4]}
  original_cursor=$(hyprctl cursorpos -j | jq -r '"\(.x) \(.y)"')
  safe_cursor=$(hyprctl monitors -j | jq -r --argjson x "$gx" --argjson y "$gy" --argjson w "$gw" --argjson h "$gh" '
    [.[] as $m | [[$m.x+8,$m.y+8],[$m.x+$m.width-8,$m.y+8],[$m.x+8,$m.y+$m.height-8],[$m.x+$m.width-8,$m.y+$m.height-8]][]
      | select(.[0] >= $m.x and .[0] < ($m.x+$m.width) and .[1] >= $m.y and .[1] < ($m.y+$m.height))
      | select(.[0] < $x or .[0] >= ($x+$w) or .[1] < $y or .[1] >= ($y+$h))]
    | first | if . then @tsv else empty end
  ')
  if [[ -n "$safe_cursor" && -n "$original_cursor" ]]; then
    safe_cursor=${safe_cursor//$'\t'/ }
    read -r safe_x safe_y <<< "$safe_cursor"
    read -r original_x original_y <<< "$original_cursor"
    move_cursor "$safe_x" "$safe_y"
    trap 'move_cursor "$original_x" "$original_y" || true' EXIT
    sleep 0.1
    grim -g "$geometry" "$file"
    move_cursor "$original_x" "$original_y"
    trap - EXIT
  else
    grim -g "$geometry" "$file"
  fi
else
  grim -g "$geometry" "$file"
fi
wl-copy < "$file"
