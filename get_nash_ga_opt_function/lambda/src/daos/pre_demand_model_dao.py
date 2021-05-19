import os
import json
import traceback
import logging

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class PredictDemandModelDao:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_path = os.getenv(
            "MODEL_PATH", "src/data/demand.json")
        self.model = self.get_model_variables()
        self.coef = self.model['coef']
        self.intercept = self.model['intercept']

    def get_model_variables(self):
        with open(self.model_path, 'r') as fp:
            return json.load(fp)
