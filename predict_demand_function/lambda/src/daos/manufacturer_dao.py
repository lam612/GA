import os
import json
import traceback
import logging

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class ManufacturerDao:
    def __init__(self):
        self.data_path = os.getenv(
            "DATA_PATH", "src/data/data.json")
        self.info = self.get_model_variables()
        self.S_p = self.info["transport"]["S_p"]
        self.T_p = self.info["transport"]["T_p"]
        self.H_p = self.info["transport"]["H_p"]
        self.p = self.info["product"]["p"]
        self.M_p = self.info["product"]["M_p"]
        self.M_s = self.info["product"]["M_s"]
        self.P = self.info["product"]["P"]
        self.C = self.info["product"]["C"]
        self.nash = self.info["nash"]
        self.NUM_OF_MATERIALS = self.info["info"]["NUM_OF_MATERIALS"]
        self.NUM_OF_RETAILERS = self.info["info"]["NUM_OF_RETAILERS"]
        self.materials = self.info["materials"]
        self.r_ids = self.info["info"]["r_ids"]

    def get_model_variables(self):
        with open(self.data_path, 'r') as fp:
            return json.load(fp)["manufacturer"]

    def get_material_cost(self):
        material_cost = sum([m["cr"] * m["M"]
                            for m in self.materials.values()])
        return material_cost
