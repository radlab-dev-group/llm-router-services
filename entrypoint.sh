#!/usr/bin/env bash
set -e

APP_SCRIPT="run_servcices.sh"
DEBUG_MODE=false

for arg in "$@"; do
    case "$arg" in
        --debug|debug|--shell|shell)
            DEBUG_MODE=true
            ;;
    esac
done

echo "[entrypoint] Working directory: $(pwd)"
echo "---"

if [ "$DEBUG_MODE" = true ]; then
    echo "[entrypoint] **Debug mode activated**. Container will stay alive for exec."
    sleep infinity
    exit 0
fi

if [ ! -f "./$APP_SCRIPT" ]; then
    echo "[entrypoint] ERROR: Application script **$APP_SCRIPT** not found!"
    exit 1
fi

echo "[entrypoint] Starting application using **$APP_SCRIPT** ..."
exec bash "./$APP_SCRIPT"