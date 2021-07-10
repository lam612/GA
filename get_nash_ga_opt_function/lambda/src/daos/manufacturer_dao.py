import os
import json
import traceback
import logging

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class ManufacturerDao:
    def __init__(self):
        self.data_path = os.getenv(
            "DATA_PATH", "/tmp/data.json")
        vmi_data = self.get_model_variables()
        mf_info = vmi_data["manufacturer"]
        self.S_p = mf_info["transport"]["S_p"]
        self.T_p = mf_info["transport"]["T_p"]
        self.H_p = mf_info["transport"]["H_p"]
        self.M_p = mf_info["transport"]
        self.P = mf_info["info"]["P"]
        self.M_p = mf_info["info"]["M_p"]
        self.M_s = mf_info["info"]["M_s"]
        self.materials = mf_info["materials"]
        self.L_farm = mf_info["lost"]["L_farm"]
        self.L_factory = mf_info["lost"]["L_factory"]
        self.p = [retailer["products"]
                  for _, retailer in vmi_data["retailer"].items()]
        self.p_rate = 1 + self.L_farm + self.L_factory
        self.NUM_OF_RETAILERS = len(vmi_data["retailer"])
        self.NUM_OF_PRODUCT = len(self.p)
        self.materials_cost = self.get_material_cost()
        self.r_ids = list(vmi_data["retailer"].keys())

    def get_model_variables(self):
        with open(self.data_path, 'r') as fp:
            return json.load(fp)

    def get_material_cost(self):
        material_cost = sum([m["cr"] * m["M"]
                            for m in self.materials.values()])
        return material_cost
