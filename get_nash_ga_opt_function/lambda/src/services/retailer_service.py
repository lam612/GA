import os
import json
import math
import traceback
import logging
from .pre_demand_service import PredictDemandModelService
from ..constants import CommonConfig

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class RetailerService:
    def __init__(self, id, K, uc, st, S_b, H_b, L_b, b_rate, T_b, products, r_num, p_num):
        self.logger = logging.getLogger(__name__)
        self.id = id
        self.K = K
        self.uc = uc
        self.st = st
        self.A = [0 for _ in range(r_num)]
        self.a = [0 for _ in CommonConfig.PRODUCT_PRICE]
        self.cp = [0 for _ in range(p_num)]
        self.S_b = S_b
        self.H_b = H_b
        self.L_b = L_b
        self.b_rate = b_rate
        self.T_b = T_b
        self.CT_fp = 0
        self.products = products
        self.p_e = CommonConfig.PRODUCT_EFFECT
        self.pre_demand_dao = PredictDemandModelService()

    def set_retailer_val(self, A, cp, a):
        self.A, self.cp, self.a = A, cp, a

    def get_total_demand(self):
        demand_list = self.pre_demand_dao.get_predict_demand(
            self.A, self.a, self.cp)
        return demand_list

    def get_retailer_demand(self):
        total_demand = 0
        demand_list = self.get_total_demand()
        for idx, p_demand in enumerate(demand_list):
            total_demand += p_demand * self.p_e[idx]
        return total_demand

    def get_retailer_profit(self):
        NP_bi = 0
        demand_list = self.get_total_demand()
        for idx, product in enumerate(self.products):
            NP_bi += demand_list[idx] * (
                product["p"] + (self.A - self.uc - self.a) * self.p_e[idx] - self.cp[idx])
        return NP_bi

    def get_m_debt(self):
        debt = 0
        demand_list = self.get_total_demand()
        for product_idx, product in enumerate(self.products):
            debt += demand_list[product_idx] * self.cp[product_idx]
        return debt

    def get_TA(self):
        TA = 0
        demand_list = self.get_total_demand()
        for idx, product in enumerate(self.products):
            TA += demand_list[idx] * \
                (self.A * self.p_e[idx])
        return TA

    def get_TTC(self):
        TTC = 0
        demand_list = self.get_retailer_demand()
        if demand_list == 0:
            return 0
        T_fee = demand_list * self.H_b
        TC_setup = self.S_b + self.L_b * self.b_rate
        self.CT_fp = math.sqrt(TC_setup / T_fee)
        return self.st * TC_setup / self.CT_fp + T_fee * self.CT_fp
