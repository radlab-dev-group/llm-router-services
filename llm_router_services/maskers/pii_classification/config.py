from typing import Optional
from dataclasses import dataclass

from llm_router_services.maskers.inference.config import MaskerModelConfig


@dataclass(frozen=True)
class PIIMaskerConfig(MaskerModelConfig):
    use_quantization: bool = True

    # F.e. mask only PERSON or all wne empty
    default_labels: Optional[list[str]] = None
