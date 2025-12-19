#!/usr/bin/env bash
# ---------------------------------------------------------------
# run_router.sh – launch the unified LLM‑Router Guardrail API
# ---------------------------------------------------------------
# Required / optional env vars (can be overridden when invoking):
#   LLM_ROUTER_API_HOST               – bind address (default: 0.0.0.0)
#   LLM_ROUTER_API_PORT               – port (default: 5000)
#
#   LLM_ROUTER_NASK_PIB_GUARD_ENABLED – “1” to expose /nask_guard
#   LLM_ROUTER_NASK_PIB_GUARD_MODEL_PATH
#   LLM_ROUTER_NASK_PIB_GUARD_DEVICE  – (-1 → CPU, 0/1 → GPU) (default: -1)
#
#   LLM_ROUTER_SOJKA_GUARD_ENABLED    – “1” to expose /sojka_guard
#   LLM_ROUTER_SOJKA_GUARD_MODEL_PATH
#   LLM_ROUTER_SOJKA_GUARD_DEVICE    – (-1 → CPU, 0/1 → GPU) (default: -1)
# ---------------------------------------------------------------

# ---- defaults -------------------------------------------------
: "${LLM_ROUTER_API_HOST:=0.0.0.0}"
: "${LLM_ROUTER_API_PORT:=5000}"

# Enable both services by default – you can turn any of them off
: "${LLM_ROUTER_NASK_PIB_GUARD_ENABLED:=0}"
: "${LLM_ROUTER_SOJKA_GUARD_ENABLED:=1}"

# Model defaults (feel free to replace with your own paths)
: "${LLM_ROUTER_NASK_PIB_GUARD_MODEL_PATH:=NASK-PIB/Herbert-PL-Guard}"
: "${LLM_ROUTER_NASK_PIB_GUARD_DEVICE:=-1}"
: "${LLM_ROUTER_SOJKA_GUARD_MODEL_PATH:=speakleash/Bielik-Guard-0.1B-v1.0}"
: "${LLM_ROUTER_SOJKA_GUARD_DEVICE:=-1}"

# ---- export so Python can read them ---------------------------
export LLM_ROUTER_API_HOST
export LLM_ROUTER_API_PORT
export LLM_ROUTER_NASK_PIB_GUARD_ENABLED
export LLM_ROUTER_SOJKA_GUARD_ENABLED
export LLM_ROUTER_NASK_PIB_GUARD_MODEL_PATH
export LLM_ROUTER_NASK_PIB_GUARD_DEVICE
export LLM_ROUTER_SOJKA_GUARD_MODEL_PATH
export LLM_ROUTER_SOJKA_GUARD_DEVICE

# ---- show what will be used ----------------------------------
echo "Starting unified LLM‑Router Guardrail API with Gunicorn:"
echo "  HOST   = $LLM_ROUTER_API_HOST"
echo "  PORT   = $LLM_ROUTER_API_PORT"
echo "  NASK Guard   = enabled=${LLM_ROUTER_NASK_PIB_GUARD_ENABLED} | device=${LLM_ROUTER_NASK_PIB_GUARD_DEVICE} | model=${LLM_ROUTER_NASK_PIB_GUARD_MODEL_PATH}"
echo "  Sojka Guard  = enabled=${LLM_ROUTER_SOJKA_GUARD_ENABLED} | device=${LLM_ROUTER_SOJKA_GUARD_DEVICE} | model=${LLM_ROUTER_SOJKA_GUARD_MODEL_PATH}"
echo

# ---- run Gunicorn --------------------------------------------
# The callable `create_app()` builds the Flask app with the enabled routes.
# Using the function syntax (`:create_app()`) makes Gunicorn invoke it.
gunicorn -w 1 -b "${LLM_ROUTER_API_HOST}:${LLM_ROUTER_API_PORT}" \
    'llm_router_services.router:create_app()'
