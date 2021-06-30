import os
import json
import traceback
import logging

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class GADao:
    def __init__(self):
        self.data_path = os.getenv(
            'DATA_PATH', '/tmp/data.json')
        self.model = self.get_model_variables()

    def get_model_variables(self):
        with open(self.data_path, 'r') as fp:
            return json.load(fp)["ga"]
