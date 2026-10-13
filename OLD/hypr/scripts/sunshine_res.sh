#!/bin/bash

# Lógica para iniciar o terminar la transmisión

if [ "$1" == "start" ]; then
    # APAGAR DP-1 y cambiar HDMI-A-1 a formato stream (1280x720)
    wlr-randr --output HDMI-A-1 --off \
              --output DP-1 --mode 1280x720@60 --pos 0,0


elif [ "$1" == "stop" ]; then
    # VOLVER HDMI-A-1 y DP-1 a sus resoluciones máximas
    # Al no especificar los Hz, Wayland aplica la máxima soportada por defecto
    wlr-randr --output HDMI-A-1 --on --mode 1920x1080@100 --pos 0,0 \
              --output DP-1 --on --mode 1920x1080@240.298996 --pos 1920,0

else
    # Mensaje de ayuda si lo ejecutas sin argumentos
  #  echo "Uso incorrecto. Ejecuta: $0 start | stop"
  echo "ta mal we"
  fi
