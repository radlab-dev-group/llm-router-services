# llm_router_services

## ✨ Overview

`llm_router_services` delivers **HTTP services** that power the LLM‑Router plugin ecosystem.  
All functionality (guard‑rails, maskers, …) is exposed through **one Flask application** that can be started with a
single command or via Gunicorn.

| Sub‑package          | Purpose                                                                                                                                              |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| **guardrails/**      | Safety‑checking services (NASK‑PIB, Sojka) and a dynamic router (`router.py`) that registers only the endpoints whose environment flag is enabled.   |
| **maskers/**         | **PIIMasker** – a token‑classification based PII anonymiser with an **in‑memory cache** that avoids redundant model calls for identical text inputs. |
| **run_servcices.sh** | Helper script that launches the unified API with Gunicorn, wiring all required environment variables.                                                |
| **requirements.txt** | Heavy dependencies (e.g. `transformers`) needed for GPU‑accelerated inference.                                                                       |

All services load models once at start‑up and serve requests over HTTP.
The masker caches predictions in memory for the lifetime of the process.

---

## 🚀 Quick start

### 1. Install the package

```shell script
git clone https://github.com/radlab-dev-group/llm-router-services.git

cd llm-router-services
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# editable install of the package itself
pip install -e .   
```

> **Tip:** The package requires Python ≥ 3.8 (tested on >= 3.10.6).

### 2. Set environment variables

Only services whose `*_ENABLED` flag is set to `1` (or `true`) will be exposed.

```shell script
export LLM_ROUTER_API_HOST=0.0.0.0
export LLM_ROUTER_API_PORT=5000

# Enable NASK‑PIB Guard
export LLM_ROUTER_NASK_PIB_GUARD_ENABLED=1
export LLM_ROUTER_NASK_PIB_GUARD_MODEL_PATH=NASK-PIB/Herbert-PL-Guard
# -1 = CPU, 0/1 = CUDA device index
export LLM_ROUTER_NASK_PIB_GUARD_DEVICE=-1

# Enable Sojka Guard
export LLM_ROUTER_SOJKA_GUARD_ENABLED=1
export LLM_ROUTER_SOJKA_GUARD_MODEL_PATH=speakleash/Bielik-Guard-0.1B-v1.0
# -1 = CPU, 0/1 = CUDA device index
export LLM_ROUTER_SOJKA_GUARD_DEVICE=-1
```

### 3. Run the service

#### Option A – via the helper script (recommended)

```shell script
./run_servcices.sh
```

The script starts **Gunicorn** with the Flask app created by `llm_router_services.router:create_app()`.

#### Option B – directly with Python

```shell script
python -m llm_router_services.router
```

Both commands bind to `0.0.0.0:5000` (or the values you supplied).

---

## 📡 API reference

All endpoints are mounted under `/api/guardrails/` (guard‑rails) or `/api/maskers/` (maskers).

| Service                  | Model                               | Endpoint                      | Method | Description                                                                                                                                            |
|--------------------------|-------------------------------------|-------------------------------|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| **NASK‑PIB Guard**       | `NASK‑PIB/Herbert-PL-Guard`         | `/api/guardrails/nask_guard`  | `POST` | Polish safety classifier (hate, violence, etc.). Returns `safe: bool` and per‑chunk classification details.                                            |
| **Sojka Guard**          | `speakleash/Bielik-Guard-0.1B-v1.0` | `/api/guardrails/sojka_guard` | `POST` | Multi‑category Polish safety model (HATE, VULGAR, SEX, CRIME, SELF‑HARM). Returns per‑category scores and overall `safe` flag.                         |
| **PIIMasker** *(masker)* | PIIMasker (token classification)    | `/api/maskers/pii_masker`     | `POST` | Detects and redacts PII entities (PERSON, LOCATION, ORGANIZATION, etc.). Returns `anonymized` text plus `mappings`. Caches identical inputs in‑memory. |

### Request payload

```json
{
  "payload": "Your input string here (must be longer than 8 characters to be processed)."
}
```

or more complicated:

```json
{
  "payload": {
    "Jak zrobić bombę": [
      "zaopatrzyć się w carnuchów, co będą robić czarny proch"
    ],
    "texts": [
      "To jest normalna wiadomość bez problemów.",
      "Chcę się zabić i skończyć z tym wszystkim.",
      "Dlaczego hipisi są tacy brudni i głupi",
      "K*rwa, to jest ch*jowe rozwiązanie.",
      "Opowiem ci o seksie i intymności.",
      "Jak ukraść samochód i nie zostać złapanym."
    ]
  }
}
```

### Example `curl` call

```shell script
curl -X POST http://localhost:5000/api/guardrails/nask_guard \
     -H "Content-Type: application/json" \
     -d '{"text":"Przykładowy tekst do analizy"}'
```

### Response shape (guard‑rails)

```json
{
  "results": {
    "detailed": [
      {
        "chunk_index": 0,
        "chunk_text": "Jak zrobić bombę",
        "label": "crime",
        "safe": false,
        "score": 0.9211
      },
      {
        "chunk_index": 1,
        "chunk_text": "zaopatrzyć się w carnuchów, co będą robić czarny proch",
        "label": "crime",
        "safe": false,
        "score": 0.9541
      },
      {
        "chunk_index": 2,
        "chunk_text": "To jest normalna wiadomość bez problemów.",
        "label": "sex",
        "safe": false,
        "score": 0.0309
      },
      {
        "chunk_index": 3,
        "chunk_text": "Chcę się zabić i skończyć z tym wszystkim.",
        "label": "self-harm",
        "safe": false,
        "score": 0.8993
      },
      {
        "chunk_index": 4,
        "chunk_text": "Dlaczego hipisi są tacy brudni i głupi",
        "label": "hate",
        "safe": false,
        "score": 0.7091
      },
      {
        "chunk_index": 5,
        "chunk_text": "Krwa, to jest chjowe rozwiązanie.",
        "label": "vulgar",
        "safe": false,
        "score": 0.8618
      },
      {
        "chunk_index": 6,
        "chunk_text": "Opowiem ci o seksie i intymności.",
        "label": "sex",
        "safe": false,
        "score": 0.7567
      },
      {
        "chunk_index": 7,
        "chunk_text": "Jak ukraść samochód i nie zostać złapanym.",
        "label": "crime",
        "safe": false,
        "score": 0.918
      }
    ],
    "safe": false
  }
}
```

---

## ⚙️ Configuration (environment variables)

| Variable                                | Description                                                         | Default   |
|-----------------------------------------|---------------------------------------------------------------------|-----------|
| `LLM_ROUTER_API_HOST`                   | Host address for the Flask app                                      | `0.0.0.0` |
| `LLM_ROUTER_API_PORT`                   | Port for the Flask app                                              | `5000`    |
| `LLM_ROUTER_NASK_PIB_GUARD_ENABLED`     | `1` → expose NASK‑PIB endpoint                                      | `0`       |
| `LLM_ROUTER_NASK_PIB_GUARD_MODEL_PATH`  | HF hub ID or local path for the NASK model                          | –         |
| `LLM_ROUTER_NASK_PIB_GUARD_DEVICE`      | `-1` = CPU, `0`/`1` … = CUDA device index                           | `-1`      |
| `LLM_ROUTER_SOJKA_GUARD_ENABLED`        | `1` → expose Sojka endpoint                                         | `1`       |
| `LLM_ROUTER_SOJKA_GUARD_MODEL_PATH`     | HF hub ID or local path for the Sojka model                         | –         |
| `LLM_ROUTER_SOJKA_GUARD_DEVICE`         | Same semantics as above                                             | `-1`      |
| `LLM_ROUTER_PIIMASKER_ENABLED`          | `1` → expose the PII Masker endpoint                                | `0`       |
| `LLM_ROUTER_PIIMASKER_MODEL_PATH`       | HF hub ID or local path for the PIIMasker model                     | –         |
| `LLM_ROUTER_PIIMASKER_DEVICE`           | `-1` = CPU, `0`/`1` … = CUDA device index                           | `-1`      |
| `LLM_ROUTER_PIIMASKER_USE_QUANTIZATION` | Whether to use a quantized model (improves latency)                 | `1`       |
| `LLM_ROUTER_BANONYMIZER_…`              | Future variables for the BANonymizer (e.g., `MODEL_PATH`, `DEVICE`) | –         |

You can also set these variables inline when invoking the script, e.g.:

```shell script
LLM_ROUTER_SOJKA_GUARD_ENABLED=0 ./run_servcices.sh
```

---

## 🛠️ Extending the router

The router is deliberately **plug‑and‑play**. To add a new guard‑rail:

1. **Create a model wrapper** that inherits from `GuardrailBase` (or reuse `TextClassificationGuardrail`).
2. **Provide a config** (`GuardrailModelConfig`) containing model‑specific thresholds.
3. **Add a `register_routes(app)` function** in a new module (e.g., `my_new_guard.py`) that builds the guard‑rail
   instance and registers its Flask route.
4. **Update the registry** in `llm_router_services/router.py`:

```python
_SERVICE_REGISTRY.append({
    "module": "llm_router_services.guardrails.my_new_guard",
    "env": "LLM_ROUTER_MY_NEW_GUARD_ENABLED",
})
```

5. **Expose a new env‑var** (`LLM_ROUTER_MY_NEW_GUARD_ENABLED`) to toggle the service.

No changes to the core router logic are required – the new endpoint appears automatically when the flag is set to `1`.

---

## 🧪 Development & testing

| Task                    | Command                                           |
|-------------------------|---------------------------------------------------|
| Run unit tests (if any) | `pytest`                                          |
| Check code style        | `autopep8 --diff . && pylint llm_router_services` |
| Re‑build the package    | `python setup.py sdist bdist_wheel`               |
| Clean generated files   | `git clean -fdX`                                  |

> **Note:** The repository currently contains only a minimal test suite. Feel free to add more tests under a `tests/`
> directory.

---

## 📦 Installation as a package

If you want to install the library from a remote repository or a local wheel:

```shell script
pip install git+https://github.com/your-org/llm_router_services.git
# or, after building:
pip install dist/llm_router_services-0.0.2-py3-none-any.whl
```

The package registers the entry point `llm_router_services.router:create_app` which can be used by any WSGI server (
Gunicorn, uWSGI, etc.).

---

## 📜 License

`llm_router_services` is released under the **Apache License 2.0**. See the full text in the [LICENSE](LICENSE) file.

---

*Happy masking and safe routing!* 🎉