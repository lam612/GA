import os
import json
import traceback
import logging

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class NashDao:
    def __init__(self):
        self.data_path = os.getenv(
            'DATA_PATH', 'src/data/data.json')
        self.nash = {}
        self.mf_id = ""
        self.alpha = 0
        self.beta = 0
        self.get_nash_variables()

    def get_nash_variables(self):
        with open(self.data_path, 'r') as fp:
            info = json.load(fp)["nash"]
        self.nash = info["weight"]
        self.mf_id = info["mf_id"]
        self.beta = info["beta"]
