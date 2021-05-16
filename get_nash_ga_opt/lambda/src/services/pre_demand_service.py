import os
import json
import traceback
import logging
from ..daos import PredictDemandModelDao

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class PredictDemandModelService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pre_demand_dao = PredictDemandModelDao()
        self.coef = self.pre_demand_dao.coef
        self.intercept = self.pre_demand_dao.intercept

    def get_predict_demand(self, A, a, cp):
        demand = A * int(self.coef[0]) + a * int(self.coef[1]) + \
            cp * int(self.coef[2]) + self.intercept
        if demand < 0:
            return 0
        return demand

    def get_total_predict(self, A, list_a, list_cp):
        return sum([self.get_predict_demand(A, list_a[i], list_cp[i]) for i in range(len(list_a))])
