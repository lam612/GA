import os
import json
import traceback
import logging
from ..daos import PredictDemandModelDao
from ..constants import CommonConfig

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class PredictDemandModelService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pre_demand_dao = PredictDemandModelDao()
        self.model = self.pre_demand_dao.model
        self.p_e = CommonConfig.PRODUCT_EFFECT

    def get_predict_demand(self, A, a, cp_list):
        demand_list = []
        for idx, cp in enumerate(cp_list):
            model_val = self.model[idx]
            p_effect = self.p_e[idx]
            demand = A * float(model_val["coef"][0]) * p_effect + a * float(
                model_val["coef"][1]) * p_effect + cp * float(model_val["coef"][2]) + model_val["intercept"]
            if demand < 0:
                demand_list.append(0)
            else:
                demand_list.append(int(demand))
        return demand_list

    def get_total_predict(self, list_A, list_a, list_cp):
        total_demand = 0
        for idx, A in enumerate(list_A):
            demand_list = self.get_predict_demand(
                list_A[idx], list_a[idx], list_cp)
            for p_idx, p_e in enumerate(self.p_e):
                total_demand += demand_list[p_idx] * p_e

        return total_demand
