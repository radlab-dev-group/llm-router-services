from typing import Optional
from dataclasses import dataclass, field

from llm_router_services.maskers.inference.config import MaskerModelConfig

DEFAULT_PII_LABELS = [
    "EVENT",
    "FACILITY",
    "LOCATION",
    "ORGANIZATION",
    "PERSON",
    "PRODUCT",
]


@dataclass(frozen=True)
class PIIMaskerConfig(MaskerModelConfig):
    _use_quantization: bool = True

    # If None or empty, default labels may be masked by the implementation.
    _default_labels: Optional[list[str]] = field(
        default_factory=lambda: DEFAULT_PII_LABELS.copy()
    )

    @property
    def use_quantization(self) -> bool:
        return self._use_quantization

    @property
    def default_labels(self) -> Optional[list[str]]:
        return self._default_labels
