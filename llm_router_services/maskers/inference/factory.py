from llm_router_plugins.maskers.pii.pii_masker_plugin import PiiMaskerPlugin

from llm_router_services.maskers.inference.config import MaskerModelConfig
from llm_router_services.maskers.pii_classification.pii_masker import PIIMasker


def create_masker(
    masker_name: str,
    model_path: str,
    device: str = "cpu",
    config: MaskerModelConfig | None = None,
):
    if masker_name == PiiMaskerPlugin.name:
        return PIIMasker(model_path=model_path, config=config, device=device)
    raise ValueError(f"Unsupported masker name: {masker_name}")


MaskerModelFactory = create_masker
