#!/bin/bash

echo "$1"

musica="/mnt/discoo/muchica"
music=()
tag="$1"

if [ -z "$tag" ]; then
    echo "pon tag"
    exit 1
fi

for archivo in "$musica"/*; do
    if [ -f "$archivo" ]; then
        x=$(getfattr -n user.mitag --only-values "$archivo" 2>/dev/null)

        if [ "$x" == "$tag" ]; then
                music+=("$archivo")
        fi
    fi
done

if [ ${#music[@]} -eq 0 ]; then
    echo "no hay"
else
    total=${#music[@]}
    ind="$((RANDOM % total))"
    canel="${music[$ind]}"
    echo "$canel"
fi