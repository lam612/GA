import os
import json
import traceback
import logging

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class RetailerDao:
    def __init__(self):
        self.data_path = os.getenv(
            'DATA_PATH', 'src/data/data.json')
        self.retailers = self.get_retailer_variables()

    def get_retailer_variables(self):
        with open(self.data_path, 'r') as fp:
            return json.load(fp)["retailer"]

    def get_retailer(self, id):
        return self.retailers[id]
