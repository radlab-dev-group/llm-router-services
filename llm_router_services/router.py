import os

from flask import Flask
from importlib import import_module

# ----------------------------------------------------------------------
# Registry of available guard‑rail services.
# Each entry maps the module that knows how to register its endpoint
# to an environment variable that toggles the service.
# ----------------------------------------------------------------------
_SERVICE_REGISTRY = [
    {
        "module": "llm_router_services.guardrails.nask.nask_pib_guard_app",
        "env": "LLM_ROUTER_NASK_PIB_GUARD_ENABLED",
    },
    {
        "module": "llm_router_services.guardrails.speakleash.sojka_guard_app",
        "env": "LLM_ROUTER_SOJKA_GUARD_ENABLED",
    },
    {
        "module": "llm_router_services.general.ping_guard_app",
    },
]


def create_app() -> Flask:
    """Build the single Flask application and register all enabled services."""
    app = Flask(__name__)

    for entry in _SERVICE_REGISTRY:
        env_var = entry.get("env")
        if env_var and os.getenv(env_var, "0") not in {"1", "true", "True"}:
            # Service disabled – skip it
            continue

        # Dynamically import the module and ask it to register its routes.
        mod = import_module(entry["module"])
        if hasattr(mod, "register_routes"):
            mod.register_routes(app)
        else:
            raise AttributeError(
                f"Module {entry['module']} does not expose `register_routes(app)`"
            )
    return app


# ----------------------------------------------------------------------
# When the file is executed directly (`python -m llm_router_services.guardrails.router`)
# start the Flask server.
# ----------------------------------------------------------------------
if __name__ == "__main__":
    _app = create_app()
    # Default host/port can be overridden with generic env vars.
    host = os.getenv("LLM_ROUTER_API_HOST", "0.0.0.0")
    port = int(os.getenv("LLM_ROUTER_API_PORT", "5000"))
    _app.run(host=host, port=port, debug=False)
