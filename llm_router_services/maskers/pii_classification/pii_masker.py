from typing import Tuple, Dict

from pii_classification.inference.inference import AnonPredictor

from llm_router_plugins.maskers.payload_interface import MaskerPayloadTraveler

from llm_router_services.maskers.inference.base import MaskerBase
from llm_router_services.maskers.inference.config import MaskerModelConfig


_GLOBAL_CACHE: Dict[str, Tuple[str, Dict]] = {}


class PIIMasker(MaskerBase, MaskerPayloadTraveler):

    def __init__(
        self, model_path: str, device: str, config: MaskerModelConfig | None = None
    ):
        super().__init__(
            config=config,
            predictor=AnonPredictor(
                model_path=model_path,
                use_quantized=config.use_quantization if config else True,
                device=device,
            ),
        )

    def _mask_text(self, text: str) -> Tuple[str, Dict]:
        if text in _GLOBAL_CACHE:
            return _GLOBAL_CACHE[text]

        res = self._predictor.predict_and_anonymize(
            text=text, labels=self._config.default_labels
        )

        if not res:
            return text, {}

        result = (res.get("text", text), res.get("mappings", {}))
        _GLOBAL_CACHE[text] = result

        return result
