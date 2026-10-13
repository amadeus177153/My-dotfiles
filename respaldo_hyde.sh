#!/usr/bin/env bash
# Respaldo portable de HyDE: configs, helpers, assets, inventarios y restaurador.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/backup.py" ]]; then
    BACKUP_TOOL="$SCRIPT_DIR/backup.py"
else
    BACKUP_TOOL="$SCRIPT_DIR/hyde-backup/backup.py"
fi
exec python3 "$BACKUP_TOOL" backup "$@"
