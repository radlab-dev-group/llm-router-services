import os
from typing import Any, Dict
from flask import Flask, request, jsonify

from llm_router_services.maskers.constants import MASKER_SERVICES_API_PREFIX
from llm_router_services.maskers.inference.base import MaskerBase
from llm_router_services.maskers.inference.factory import MaskerModelFactory
from llm_router_services.maskers.pii_classification.config import PIIMaskerConfig

_ENV_PREFIX = "LLM_ROUTER_PII_MASKER_"


def _build_masker():
    model_path = os.getenv(f"{_ENV_PREFIX}MODEL_PATH")
    if not model_path:
        raise RuntimeError(
            f"PII masker model path not set – export {_ENV_PREFIX}MODEL_PATH"
        )
    device = os.getenv(f"{_ENV_PREFIX}DEVICE", "cpu")

    return MaskerModelFactory(
        masker_name="pii_masker",
        model_path=model_path,
        device=device,
        config=PIIMaskerConfig(),
    )


def register_routes(app: Flask) -> None:
    masker = _build_masker()

    @app.route(f"{MASKER_SERVICES_API_PREFIX}/pii", methods=["POST"])
    def pii_mask_endpoint():
        if not request.is_json:
            return jsonify({"error": "Request body must be JSON"}), 400

        payload: Dict[str, Any] = request.get_json()
        try:
            return MaskerBase.call_and_return_masker_result(
                f_map=masker.mask_payload, payload=payload
            )
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500
