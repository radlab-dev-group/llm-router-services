import os
from typing import Any, Dict

from flask import Flask, request, jsonify

from llm_router_services.guardrails.constants import SERVICES_API_PREFIX
from llm_router_services.guardrails.inference.factory import (
    GuardrailClassifierModelFactory,
)
from llm_router_services.guardrails.speakleash.config import SojkaModelConfig

# -----------------------------------------------------------------------
# Environment prefix – all configuration keys start with this value
# -----------------------------------------------------------------------
_ENV_PREFIX = "LLM_ROUTER_SOJKA_GUARD_"

app = Flask(__name__)

MODEL_PATH = os.getenv(f"{_ENV_PREFIX}MODEL_PATH", None)
if not MODEL_PATH:
    raise Exception(
        f"Sojka guardrail model path is not set! "
        f"Export {_ENV_PREFIX}MODEL_PATH with proper model path"
    )

# Keep only a single constant for the device (CPU by default)
DEFAULT_DEVICE = os.getenv(f"{_ENV_PREFIX}DEVICE")
if DEFAULT_DEVICE:
    DEFAULT_DEVICE = int(DEFAULT_DEVICE)

# -----------------------------------------------------------------------
# Build the guardrail object via the factory, passing the Sojka‑specific config
# -----------------------------------------------------------------------
guardrail = GuardrailClassifierModelFactory(
    model_type="text_classification",
    model_path=MODEL_PATH,
    device=DEFAULT_DEVICE,
    config=SojkaModelConfig(),
)


# -----------------------------------------------------------------------
# Endpoint: POST /api/guardrails/sojka_guard
# -----------------------------------------------------------------------
@app.route(f"{SERVICES_API_PREFIX}/sojka_guard", methods=["POST"])
def sojka_guardrail():
    """
    Accepts a JSON payload, classifies the content and returns the aggregated results.
    """
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400

    payload: Dict[str, Any] = request.get_json()
    try:
        results = guardrail.classify_chunks(payload)
        return jsonify({"results": results}), 200
    except Exception as exc:  # pragma: no cover – safety net
        return jsonify({"error": str(exc)}), 500


# -----------------------------------------------------------------------
# Run the Flask server (only when executed directly)
# -----------------------------------------------------------------------
if __name__ == "__main__":
    host = os.getenv(f"{_ENV_PREFIX}FLASK_HOST", "0.0.0.0")
    port = int(os.getenv(f"{_ENV_PREFIX}FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=False)
