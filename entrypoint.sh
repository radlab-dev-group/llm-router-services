#!/usr/bin/env bash
set -e

APP_SCRIPT=""
DEBUG_MODE=false
SELECTED_APP=false

for arg in "$@"; do
    case "$arg" in
        --debug|debug|--shell|shell)
            DEBUG_MODE=true
            ;;
        --nask|nask)
            APP_SCRIPT="run_nask_guardrail.sh"
            SELECTED_APP=true
            ;;
        --sojka|sojka)
            APP_SCRIPT="run_sojka_guardrail.sh"
            SELECTED_APP=true
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

if [ "$SELECTED_APP" = false ]; then
    echo "[entrypoint] ERROR: No application script selected!"
    echo "[entrypoint] USAGE: Pass one of the required arguments: **--nask** or **--sojka**."
    exit 1
fi

if [ ! -f "./$APP_SCRIPT" ]; then
    echo "[entrypoint] ERROR: Application script **$APP_SCRIPT** not found!"
    exit 1
fi

echo "[entrypoint] Starting application using **$APP_SCRIPT** ..."
exec "./$APP_SCRIPT"