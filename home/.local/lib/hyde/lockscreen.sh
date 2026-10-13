#!/usr/bin/env bash
[[ $HYDE_SHELL_INIT -ne 1 ]] && eval "$(hyde-shell init)"
lockscreen="${HYPRLAND_LOCKSCREEN:-hyprlock}"
lockscreen="${LOCKSCREEN:-$lockscreen}"
lockscreen="${HYDE_LOCKSCREEN:-$lockscreen}"
# Use the installed locker when the default Hyprlock is unavailable.
if [[ "$lockscreen" == "hyprlock" ]] && ! command -v hyprlock >/dev/null 2>&1 && command -v swaylock >/dev/null 2>&1; then
    lockscreen="swaylock"
fi
source "${LIB_DIR}/hyde/shutils/argparse.sh"
argparse_init "$@"
argparse_program "hyde-shell lockscreen"
argparse_header "HyDE Lockscreen Launcher"
argparse "--get" "" "Get the current lockscreen command"
argparse_finalize

case $ARGPARSE_ACTION in
    get) echo "$lockscreen" && exit 0 ;;
esac

unit_name="hyde-lockscreen.service"
if [[ "$lockscreen" == "swaylock" ]]; then
    args=(--daemonize --clock --effect-blur 6x3)
    wallpaper="${HYDE_CACHE_HOME:-$HOME/.cache/hyde}/wall.set"
    [[ -f "$wallpaper" ]] && args+=(--image "$wallpaper" --scaling fill)
    exec swaylock "${args[@]}" "$@"
fi
args=(-u "$unit_name" -t service)
if which "$lockscreen.sh" 2> /dev/null 1>&2; then
    printf "Executing $lockscreen wrapper script : %s\n" "$lockscreen.sh"
    app.sh "${args[@]}" -- "$lockscreen.sh" "$@"
else
    printf "Executing raw command: %s\n" "$lockscreen"
    app.sh "${args[@]}" -- "$lockscreen" "$@"
fi
