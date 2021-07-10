import os
import json
import traceback
import logging
from ..constants import CommonConfig

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class NashDao:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_path = os.getenv(
            'DATA_PATH', '/tmp/data.json')
        self.nash = {}
        self.mf_id = ""
        self.alpha = 0
        self.beta = CommonConfig.NASH_GA_BETA
        self.get_nash_variables()

    def get_nash_variables(self):
        with open(self.data_path, 'r') as fp:
            info = json.load(fp)["nash"]
        self.nash = info["weight"]
        self.mf_id = info["mf_id"]
