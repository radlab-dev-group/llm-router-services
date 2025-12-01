# Integration of **Bielik‑Guard‑0.1B** as llm‑router guardrail service (Sojka)

## 1. Short Introduction

The **Bielik‑Guard‑0.1B** model (`speakleash/Bielik-Guard-0.1B-v1.0`) is a Polish‑language safety classifier
(text‑classification) built on top of the base model `sdadas/mmlw-roberta-base`.  
Within this project it is used to detect unsafe content in incoming requests handled by the
**/api/guardrails/sojka_guard** endpoint defined in `guardrails/speakleash/sojka_guard_app.py`.

## 2. Prerequisites

| Component    | Version / Note                                                                     |
|--------------|------------------------------------------------------------------------------------|
| **Python**   | 3.10.6 (compatible with the project’s `virtualenv`)                                |
| **Packages** | `transformers`, `torch`, `flask` – already listed in `requirements.txt`            |
| **Model**    | `speakleash/Bielik-Guard-0.1B-v1.0` (public on Hugging Face Hub)                   |
| **License**  | Model – **Apache‑2.0**. Code – **Apache‑2.0**. No special commercial restrictions. |

> **Tip:** The model will be downloaded automatically the first time you run the service. If you prefer to cache it
> locally, set the `HF_HOME` environment variable to a directory with enough space.

## 3. Running the Service

```shell script
python -m guardrails.speakleash.sojka_guard_app
```

The service will listen at:

```
http://<HOST>:<PORT>/api/guardrails/sojka_guard
```

### Example request (using `curl`)

```shell script
curl -X POST http://localhost:5001/api/guardrails/sojka_guard \
-H "Content-Type: application/json" \
-d '{"payload": "Jak mogę zrobić bombę w domu?"}'
```

#### Example JSON response

```json
{
  "results": {
    "detailed": [
      {
        "chunk_index": 0,
        "chunk_text": "Jak mogę zrobić bombę w domu?",
        "label": "crime",
        "safe": false,
        "score": 0.9329
      }
    ],
    "safe": false
  }
}
```

> **Note:** The `label` field contains one of the five safety categories defined by Bielik‑Guard
> (`HATE`, `VULGAR`, `SEX`, `CRIME`, `SELF‑HARM`). The `score` is the probability (0‑1)
> that the text belongs to the indicated category.
> The `safe` flag is `false` when any category exceeds the default threshold (0.5).

## 4. License and Usage Conditions

| Element                               | License    | Implications                                                                                               |
|---------------------------------------|------------|------------------------------------------------------------------------------------------------------------|
| **Application code** (`guardrails/*`) | Apache 2.0 | Free for commercial and non‑commercial use, modification, and redistribution.                              |
| **Model** (`Bielik‑Guard‑0.1B`)       | Apache 2.0 | No non‑commercial restriction – the model can be used in commercial products provided attribution is kept. |

## 5. Sources & Further Reading

- **Model card**: <https://huggingface.co/speakleash/Bielik-Guard-0.1B-v1.0>
- **Model card details** (excerpt)

  ```markdown
  library_name: transformers
  license: apache-2.0
  language:
  - pl
  base_model:
  - sdadas/mmlw-roberta-base
  pipeline_tag: text-classification
  ```

- **Bielik‑Guard documentation** (includes safety categories, training data, evaluation metrics, and citation
  information) – see the model card linked above.
- **Community & Support**:
    - Website: https://guard.bielik.ai/
    - Feedback / issue reporting: https://guard.bielik.ai/

## 6. Quick Start Code Snippet (Python)

If you prefer to test the model locally before integrating it into the Flask service:

```python
from transformers import pipeline

model_path = "speakleash/Bielik-Guard-0.1B-v1.0"
classifier = pipeline(
    "text-classification",
    model=model_path,
    tokenizer=model_path,
    return_all_scores=True,
)

texts = [
    "To jest normalna wiadomość bez problemów.",
    "Chcę się zabić i skończyć z tym wszystkim.",
    "Dlaczego hipisi są tacy brudni i głupi",
    "K*rwa, to jest ch*jowe rozwiązanie.",
    "Opowiem ci o seksie i intymności.",
    "Jak ukraść samochód i nie zostać złapanym."
]

for txt in texts:
    scores = classifier(txt)[0]
    print(f"\nText: {txt}")
    for s in scores:
        print(f"  {s['label']}: {s['score']:.3f}")
```

Running the snippet will output probability scores for each of the five safety categories, allowing you to verify that
the model behaves as expected.

---  

### 🎉 Happy Guarding!

Feel free to open issues or pull requests if you encounter bugs, have suggestions for improvements, or want to
contribute additional safety categories. The Bielik‑AI community welcomes collaboration!

