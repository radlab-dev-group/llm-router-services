# Guardrails Package

`guardrails` provides the core safety‑checking and masking services used by **llm‑router**. Each service runs as a small
Flask application exposing a simple HTTP API that can be called by the corresponding plugin.

## Sub‑packages

| Sub‑package                           | Purpose                                                                                                 |
|---------------------------------------|---------------------------------------------------------------------------------------------------------|
| **guardrails/guardrails/**            | Abstract base classes, factory, configuration objects and payload handling logic.                       |
| **guardrails/guardrails/nask/**       | NASK‑PIB safety model (Polish text classification).                                                     |
| **guardrails/guardrails/speakleash/** | Sojka (Bielik‑Guard) safety model (multi‑category).                                                     |
| **guardrails/maskers/**               | **UNDER DEVELOPMENT** Token‑classification based anonymiser (BANonymizer).                              |
| **run_*.sh** scripts                  | Convenience wrappers to start each Flask service (Gunicorn for guardrails, plain Flask for the masker). |

## HTTP API

All guardrail endpoints share the same request format:

```json
{
  "payload": <any
  JSON
  value>
}
```

* `payload` may be a string, object, list, or any JSON‑serialisable type.
* The service extracts all textual elements longer than 8 characters and runs them through the model.
* The response contains an overall `safe` flag and a `detailed` list with per‑chunk (or per‑category) scores.

## Guardrail Services Documentation

- **NASK‑PIB Guardrail** – detailed usage, examples, and licensing information:  
  [guardrails/nask/README.md](nask/README.md)

- **Sojka Guardrail** – detailed usage, examples, and licensing information:  
  [guardrails/speakleash/README.md](speakleash/README.md)