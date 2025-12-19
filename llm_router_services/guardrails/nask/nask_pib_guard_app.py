# llm_router_services/guardrails/nask/nask_pib_guard_app.py
import os
from typing import Any, Dict

from flask import Flask, request, jsonify

from llm_router_services.guardrails.constants import SERVICES_API_PREFIX
from llm_router_services.guardrails.inference.factory import (
    GuardrailClassifierModelFactory,
)
from llm_router_services.guardrails.nask.config import NaskModelConfig

_ENV_PREFIX = "LLM_ROUTER_NASK_PIB_GUARD_"


# ----------------------------------------------------------------------
# Helper: build the Guardrail instance (used both by the old script
# and the new router).  Keeping it in a function makes the code reusable.
# ----------------------------------------------------------------------
def _build_guardrail() -> GuardrailClassifierModelFactory:
    model_path = os.getenv(f"{_ENV_PREFIX}MODEL_PATH")
    if not model_path:
        raise RuntimeError(
            f"NASK‑PIB guardrail model path not set – export {_ENV_PREFIX}MODEL_PATH"
        )
    device = os.getenv(f"{_ENV_PREFIX}DEVICE")
    device = int(device) if device else -1

    return GuardrailClassifierModelFactory(
        model_type="text_classification",
        model_path=model_path,
        device=device,
        config=NaskModelConfig(),
    )


# ----------------------------------------------------------------------
# Public function used by the central router to attach the endpoint.
# ----------------------------------------------------------------------
def register_routes(app: Flask) -> None:
    """Register the /nask_guard endpoint on the given Flask app."""
    guardrail = _build_guardrail()

    @app.route(f"{SERVICES_API_PREFIX}/nask_guard", methods=["POST"])
    def nask_guardrail():
        """Handle a JSON payload and return guard‑rail results."""
        if not request.is_json:
            return jsonify({"error": "Request body must be JSON"}), 400

        payload: Dict[str, Any] = request.get_json()
        try:
            results = guardrail.classify_chunks(payload)
            return jsonify({"results": results}), 200
        except Exception as exc:  # pragma: no cover – safety net
            return jsonify({"error": str(exc)}), 500
