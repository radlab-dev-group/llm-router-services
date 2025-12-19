"""
Simple health‑check endpoint for the guardrails service.

Provides:
    GET /api/guardrails/ping -> {"pong": "pong"}
"""

from flask import Flask, jsonify

from llm_router_services.guardrails.constants import SERVICES_API_PREFIX


def register_routes(app: Flask) -> None:
    """Register the /ping endpoint on the given Flask app."""

    @app.route(f"{SERVICES_API_PREFIX}/ping", methods=["GET"])
    def ping():
        # Very small payload – just confirm the service is alive.
        return jsonify({"response": "pong"}), 200
