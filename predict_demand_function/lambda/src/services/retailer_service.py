import os
import json
import math
import traceback
import logging
from .pre_demand_service import PredictDemandModelService

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class RetailerService:
    def __init__(self, id, K, uc, A, a, cp, p, S_b, H_b, L_b, b_rate, T_b):
        self.logger = logging.getLogger(__name__)
        self.id = id
        self.K = K
        self.uc = uc
        self.A = A
        self.a = a
        self.cp = cp
        self.p = p
        self.S_b = S_b
        self.H_b = H_b
        self.L_b = L_b
        self.b_rate = b_rate
        self.T_b = T_b
        self.CT_fp = 0
        self.pre_demand_dao = PredictDemandModelService()

    def set_retailer_val(self, A, a, cp):
        self.A, self.a, self.cp = A, a, cp

    def get_retailer_demand(self):
        return self.pre_demand_dao.get_predict_demand(self.A, self.a, self.cp)

    def get_retailer_profit(self):
        NP_bi = self.get_retailer_demand() * (self.p - self.cp - self.uc - self.a)
        return NP_bi

    def get_m_debt(self):
        return self.get_retailer_demand() * (self.cp + self.uc)

    def get_total_m_ads(self):
        return self.get_retailer_demand() * (self.A)

    def get_TTC(self):
        r_demand = self.get_retailer_demand()
        if r_demand == 0:
            return 0
        T_fee = self.get_retailer_demand() * self.H_b
        TC_setup = self.S_b + self.L_b * self.b_rate
        self.CT_fp = math.sqrt(TC_setup / T_fee)
        return TC_setup / self.CT_fp + T_fee * self.CT_fp
