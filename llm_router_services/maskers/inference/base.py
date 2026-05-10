from abc import ABC
from flask import jsonify


class MaskerBase(ABC):
    def __init__(self, config, predictor):
        self._config = config
        self._predictor = predictor

    @staticmethod
    def call_and_return_masker_result(f_map, payload):
        anon_payload, mappings = f_map(payload)
        return jsonify({"anonymized": anon_payload, "mappings": mappings}), 200
