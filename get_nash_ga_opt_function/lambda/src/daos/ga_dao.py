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
        self.g_num = self.model["generation_number"]
        self.p_size = self.model["population_size"]
        self.s_rate = self.model["selection_rate"]
        self.c_rate = self.model["crossover_rate"]
        self.m_rate = self.model["mutation_rate"]
        self.MAX_A = self.model["MAX_A"]
        self.MAX_a = self.model["MAX_a"]

    def get_model_variables(self):
        with open(self.data_path, 'r') as fp:
            return json.load(fp)["ga"]
