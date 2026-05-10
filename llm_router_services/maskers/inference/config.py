from abc import ABC, abstractmethod


class MaskerModelConfig(ABC):

    @property
    @abstractmethod
    def use_quantization(self) -> bool: ...

    @property
    @abstractmethod
    def default_labels(self) -> list[str]: ...
