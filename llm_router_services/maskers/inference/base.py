from typing import Any, Dict, Tuple
from abc import ABC, abstractmethod

from llm_router_plugins.maskers.payload_interface import MaskerPayloadTraveler


class MaskerBase(ABC):
    def __init__(self, config, predictor):
        self._config = config
        self._predictor = predictor
