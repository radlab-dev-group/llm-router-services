from __future__ import annotations

from dataclasses import dataclass

from llm_router_services.guardrails.inference.config import GuardrailModelConfig


@dataclass(frozen=True)
class SojkaModelConfig(GuardrailModelConfig):
    pipeline_batch_size: int = 64
    min_score_for_safe: float = 0.5
    min_score_for_not_safe: float = 0.7
