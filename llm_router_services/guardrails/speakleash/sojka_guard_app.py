# llm_router_services/guardrails/speakleash/sojka_guard_app.py
import os
from typing import Any, Dict

from flask import Flask, request, jsonify

from llm_router_services.guardrails.constants import SERVICES_API_PREFIX
from llm_router_services.guardrails.inference.factory import (
    GuardrailClassifierModelFactory,
)
from llm_router_services.guardrails.speakleash.config import SojkaModelConfig

_ENV_PREFIX = "LLM_ROUTER_SOJKA_GUARD_"


def _build_guardrail():
    model_path = os.getenv(f"{_ENV_PREFIX}MODEL_PATH")
    if not model_path:
        raise RuntimeError(
            f"Sojka guardrail model path not set – export {_ENV_PREFIX}MODEL_PATH"
        )
    device = os.getenv(f"{_ENV_PREFIX}DEVICE")
    device = int(device) if device else -1

    return GuardrailClassifierModelFactory(
        model_type="text_classification",
        model_path=model_path,
        device=device,
        config=SojkaModelConfig(),
    )


def register_routes(app: Flask) -> None:
    """Register the /sojka_guard endpoint on the given Flask app."""
    guardrail = _build_guardrail()

    @app.route(f"{SERVICES_API_PREFIX}/sojka_guard", methods=["POST"])
    def sojka_guardrail():
        """Handle a JSON payload and return guard‑rail results."""
        if not request.is_json:
            return jsonify({"error": "Request body must be JSON"}), 400

        payload: Dict[str, Any] = request.get_json()
        try:
            results = guardrail.classify_chunks(payload)
            return jsonify({"results": results}), 200
        except Exception as exc:  # pragma: no cover – safety net
            return jsonify({"error": str(exc)}), 500
