# llm_router_services

## ✨ Overview

`llm_router_services` provides **HTTP services** that implement the core functionality used by the LLM‑Router’s plugin
system.  
The services expose guard‑rail and masking capabilities through a **single Flask application** that can be started with
one command.

Key components:

| Sub‑package          | Primary purpose                                                                                                                                                          |
|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **guardrails/**      | Implements safety‑checking services (NASK‑PIB and Sojka) and a dynamic **router** (`router.py`) that discovers which endpoints to expose based on environment variables. |
| **maskers/**         | Contains the **BANonymizer** (`banonymizer.py` – **under development**) – a lightweight Flask service that performs token‑classification based anonymisation.            |
| **run_router.sh**    | Convenience wrapper that starts the unified API with Gunicorn, handling all required environment variables.                                                              |
| **requirements.txt** | Lists heavy dependencies (e.g., `transformers`) required for GPU‑accelerated inference.                                                                                  |

All services are **stateless**; they load their models once at start‑up and then serve requests over HTTP.

---

## 🛡️ Guardrails (Unified API)

The guard‑rail sub‑package now offers a **single entry point** (`/api/guardrails/*`) that dynamically registers the
enabled endpoints.  
The design makes it trivial to add new guard‑rails – just implement a `register_routes(app)` function and add the module
to the registry.

| Service                  | Model                               | Endpoint                           | Description                                                                                                                                    |
|--------------------------|-------------------------------------|------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| **NASK‑PIB Guard**       | `NASK‑PIB/HerBERT‑PL‑Guard`         | `POST /api/guardrails/nask_guard`  | Polish‑language safety classifier detecting unsafe content (e.g., hate, violence). Returns a `safe` flag and per‑chunk classification details. |
| **Sojka Guard**          | `speakleash/Bielik‑Guard‑0.1B‑v1.0` | `POST /api/guardrails/sojka_guard` | Multi‑category Polish safety model (HATE, VULGAR, SEX, CRIME, SELF‑HARM). Returns detailed scores per category and an overall `safe` flag.     |
| **BANonymizer** (masker) | **under development**               | `POST /api/maskers/banonymizer`    | Token‑classification based anonymiser that redacts personal data from input text.                                                              |

### How to use

1. **Start the unified service** – run the provided shell script (`run_router.sh`) or invoke the module directly:

```bash
python -m llm_router_services.router
```

2. **Send a JSON payload** – the request body must be a JSON object; any string fields longer than 8 characters are
   extracted and classified/anonymised.

3. **Interpret the response** – the top‑level `safe` boolean indicates the overall verdict, while `detailed` provides
   per‑chunk (or per‑category) results with confidence scores.

### Configuration (environment variables)

All guard‑rail services are controlled through **`LLM_ROUTER_…`** prefixed variables.  
Only the services whose `*_ENABLED` flag is set to `1` (or `true`) are registered.

| Prefix                                 | Meaning (applies to both NASK and Sojka)                                      |
|----------------------------------------|-------------------------------------------------------------------------------|
| `LLM_ROUTER_API_HOST`                  | Host address for the unified Flask app (default: `0.0.0.0`).                  |
| `LLM_ROUTER_API_PORT`                  | Port for the unified Flask app (default: `5000`).                             |
| `LLM_ROUTER_NASK_PIB_GUARD_ENABLED`    | Set to `1` to expose `/api/guardrails/nask_guard`.                            |
| `LLM_ROUTER_NASK_PIB_GUARD_MODEL_PATH` | Hugging‑Face hub identifier or local path for the NASK‑PIB model.             |
| `LLM_ROUTER_NASK_PIB_GUARD_DEVICE`     | `-1` for CPU, `0`/`1`… for CUDA device index (default: `-1`).                 |
| `LLM_ROUTER_SOJKA_GUARD_ENABLED`       | Set to `1` to expose `/api/guardrails/sojka_guard`.                           |
| `LLM_ROUTER_SOJKA_GUARD_MODEL_PATH`    | Hub identifier or local path for the Sojka model.                             |
| `LLM_ROUTER_SOJKA_GUARD_DEVICE`        | Same semantics as above for the Sojka model (default: `-1`).                  |
| `LLM_ROUTER_BANONYMIZER_…`             | (Future) variables for the BANonymizer masker (e.g., `MODEL_PATH`, `DEVICE`). |

#### Example – enable both guard‑rails

```bash
export LLM_ROUTER_NASK_PIB_GUARD_ENABLED=1
export LLM_ROUTER_NASK_PIB_GUARD_MODEL_PATH=NASK-PIB/Herbert-PL-Guard
export LLM_ROUTER_NASK_PIB_GUARD_DEVICE=-1

export LLM_ROUTER_SOJKA_GUARD_ENABLED=1
export LLM_ROUTER_SOJKA_GUARD_MODEL_PATH=speakleash/Bielik-Guard-0.1B-v1.0
export LLM_ROUTER_SOJKA_GUARD_DEVICE=-1

export LLM_ROUTER_API_HOST=0.0.0.0
export LLM_ROUTER_API_PORT=5000
```

### Extensibility

The guard‑rail architecture is built around the **`GuardrailBase`** abstract class and a **factory** (
`GuardrailClassifierModelFactory`).  
To add a new safety model:

1. Implement a concrete subclass of `GuardrailBase` (or reuse `TextClassificationGuardrail`).
2. Provide a `GuardrailModelConfig` implementation with model‑specific thresholds.
3. Add a `register_routes(app)` function in a new module that builds the guard‑rail instance and registers its endpoint.
4. Add the module to `_SERVICE_REGISTRY` in `router.py` together with an enable‑flag env‑var (e.g.,
   `LLM_ROUTER_NEW_GUARD_ENABLED`).

No changes to the core router are required – the system will automatically expose the new endpoint when the flag is set.

---

## 📜 License

See the [LICENSE](LICENSE) file.

---

*Happy masking and safe routing!* 🎉
