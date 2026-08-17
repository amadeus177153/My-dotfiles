#!/bin/bash

if hyprctl activewindow -j| jq -r.class| grep -iq \"steam\" ; then hyprctl dispatch killactive \"\" ; else steam; fi
