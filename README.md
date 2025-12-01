# llm_router_services

## ✨ Overview

`llm_router_services` provides **HTTP services** that implement the core functionality used by the LLM‑Router’s plugin
system.  
The services expose guardrail and masking capabilities through Flask applications
that can be called by the corresponding plugins in `llm_router_plugins`.

Key components:

| Sub‑package              | Primary purpose                                                                                                                                                                                                                    |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **guardrails/**          | Hosts the NASK‑PIB guardrail service (`nask_pib_guard_app.py`). It receives a JSON payload, chunks the text, runs a Hugging‑Face classification pipeline, and returns a safety verdict (`safe` flag + detailed per‑chunk results). |
| **maskers/**             | Contains the **BANonymizer** (`banonymizer.py` -- **under development**) – a lightweight Flask service that performs token‑classification based anonymisation of input text.                                                       |
| **run_*.sh** scripts     | Convenience wrappers to start the services (Gunicorn for the guardrail, plain Flask for the anonymiser).                                                                                                                           |
| **requirements‑gpu.txt** | Lists heavy dependencies (e.g., `transformers`) required for GPU‑accelerated inference.                                                                                                                                            |

The services are **stateless**; they load their models once at start‑up and then serve requests over HTTP.

---

## 🛡️ Guardrails

Full documentation for the guardrails sub‑package is available
in [guardrail-readme](llm_router_services/guardrails/README.md).

The **guardrail** sub‑package implements safety‑checking services that can be queried via HTTP:

| Service                  | Model                               | Endpoint                           | Description                                                                                                                                    |
|--------------------------|-------------------------------------|------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| **NASK‑PIB Guard**       | `NASK‑PIB/HerBERT‑PL‑Guard`         | `POST /api/guardrails/nask_guard`  | Polish‑language safety classifier detecting unsafe content (e.g., hate, violence). Returns a `safe` flag and per‑chunk classification details. |
| **Sojka Guard**          | `speakleash/Bielik‑Guard‑0.1B‑v1.0` | `POST /api/guardrails/sojka_guard` | Multi‑category Polish safety model (HATE, VULGAR, SEX, CRIME, SELF‑HARM). Returns detailed scores per category and an overall `safe` flag.     |
| **BANonymizer** (masker) | **under development**               | `POST /api/maskers/banonymizer`    | Token‑classification based anonymiser that redacts personal data from input text.                                                              |

### How to use

1. **Start the service** – run the provided shell script (`run_*_guardrail.sh` or `run_*_masker.sh`) or invoke the Flask
   module directly (e.g., `python -m llm_router_services.guardrails.speakleash.sojka_guard_app`).
2. **Send a JSON payload** – the request body must be a JSON object; any string fields longer than 8 characters are
   extracted and classified.
3. **Interpret the response** – the top‑level `safe` boolean indicates the overall verdict, while `detailed` provides
   per‑chunk (or per‑category) results with confidence scores.

### Configuration

All guardrail services read configuration from environment variables prefixed with:

* `LLM_ROUTER_NASK_PIB_GUARD_` – for the NASK‑PIB guardrail.
* `LLM_ROUTER_SOJKA_GUARD_` – for the Sojka guardrail.
* `LLM_ROUTER_BANONYMIZER_` – for the masker.

Key variables include:

* `MODEL_PATH` – path or Hugging‑Face hub identifier of the model.
* `DEVICE` – `-1` for CPU or CUDA device index for GPU inference.
* `FLASK_HOST` / `FLASK_PORT` – network binding for the Flask server.

### Extensibility

The guardrail architecture is built around the **`GuardrailBase`** abstract class and a **factory** (
`GuardrailClassifierModelFactory`). To add a new safety model:

1. Implement a concrete subclass of `GuardrailBase` (or reuse `TextClassificationGuardrail`).
2. Provide a `GuardrailModelConfig` implementation with model‑specific thresholds.
3. Register the model type in the factory if a new identifier is required.

---

## 📜 License

See the [LICENSE](LICENSE) file.

---

*Happy masking and safe routing!*
