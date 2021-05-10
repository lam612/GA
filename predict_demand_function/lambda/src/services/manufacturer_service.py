import os
import json
import math
import traceback
import logging
from ..daos import RetailerDao, ManufacturerDao
from .retailer_service import RetailerService

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class ManufacturerService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.retailer_dao = RetailerDao()
        self.mft_dao = ManufacturerDao()
        self.S_p = self.mft_dao.S_p
        self.T_p = self.mft_dao.T_p
        self.H_p = self.mft_dao.H_p
        self.p = self.mft_dao.p
        self.M_p = self.mft_dao.M_p
        self.M_s = self.mft_dao.M_s
        self.P = self.mft_dao.P
        self.C = self.mft_dao.C
        self.materials = self.mft_dao.materials
        self.nash = self.mft_dao.nash
        self.NUM_OF_MATERIALS = self.mft_dao.NUM_OF_MATERIALS
        self.NUM_OF_RETAILERS = self.mft_dao.NUM_OF_RETAILERS
        self.r_ids = self.mft_dao.r_ids
        self.retailers = self.get_retailers()
        self.CT_fp = 0
        self.total_demand = 0

    def get_retailers(self):
        retailers = []
        for id in self.r_ids:
            r_info = self.retailer_dao.get_retailer(id)
            retailer = RetailerService(r_info["id"], r_info["K"], r_info["uc"], r_info["A"], r_info["a"],
                                       r_info["cp"], r_info["p"], r_info["S_b"], r_info["H_b"], r_info["L_b"], r_info["b_rate"], r_info["T_b"])
            retailers.append(retailer)
        return retailers

    def get_retailer(self, r_id):
        for retailer in self.retailers:
            if retailer.id == r_id:
                return retailer

    def get_retailer_demand(self, r_id):
        return self.get_retailer(r_id).get_retailer_demand()

    def set_total_demand(self):
        self.total_demand = sum(
            [retailer.get_retailer_demand() for retailer in self.retailers])

    def get_r_profit(self, r_id):
        return self.get_retailer(r_id).get_retailer_profit()

    def get_total_r_profit(self):
        return sum([retailer.get_retailer_profit() for retailer in self.retailers])

    def get_nash_ga_fitness(self):
        fitness = self.get_m_profit() * self.nash["manufacturer"]["weight"]
        rtl_weight = self.nash["retailer"]
        rtl_fitness = sum([rtl_weight[retailer.id]["weight"] *
                          retailer.get_retailer_profit() for retailer in self.retailers])
        # for retailer in self.retailers:
        #     print(retailer.get_retailer_profit())
        #     print(rtl_weight[retailer.id]["weight"])
        fitness += rtl_fitness
        # print(rtl_fitness)
        return fitness

    def get_m_profit(self):
        self.set_total_demand()
        NP_M = self.get_TR_M() - self.get_TC_M()
        return NP_M

    def get_total_profit(self):
        return self.get_total_r_profit() + self.get_m_profit()

    def get_total_m_ads(self):
        total_m_ads = sum([retailer.get_total_m_ads()
                          for retailer in self.retailers])
        return total_m_ads

    def get_TR_M(self):
        TR_M = sum([retailer.get_m_debt() for retailer in self.retailers])
        return TR_M

    def get_TC_M(self):
        TC_M = self.get_TDC_M() + self.get_TIDC_M()
        return TC_M

    def get_TDC_M(self):
        material_cost = self.mft_dao.get_material_cost()
        direct_cost_per_unit = material_cost + self.M_p + self.M_s
        TDC_M = self.total_demand * direct_cost_per_unit
        return TDC_M

    def get_TIDC_M(self):
        TIDC_M = self.get_TIC() + self.get_TTC() + self.get_total_m_ads()
        return TIDC_M

    def get_TIC(self):
        TIC = self.get_TIC_r() + self.get_TIC_fp()
        return TIC

    def get_TTC(self):
        TTC = self.get_TTC_r() + self.get_TTC_fp() + self.get_TTC_b()
        return TTC

    def get_TTC_r(self):
        TTC_r = 0
        for material in self.materials.values():
            T_fee = self.total_demand * material["M"] * material["T_r"]
            CT_r = math.sqrt(material["S_r"] / T_fee)
            TTC_r += material["S_r"] / CT_r + T_fee * CT_r
        return TTC_r

    def get_TIC_r(self):
        TIC = 0
        for material in self.materials.values():
            TIC += (material["n"] + 1) * self.total_demand * \
                material["M"] * material["H_r"] / 2
        return TIC

    def get_TTC_fp(self):
        T_fee = self.total_demand * self.T_p
        self.CT_fp = math.sqrt(self.S_p / T_fee)
        TTC_fp = self.S_p / self.CT_fp + T_fee * self.CT_fp
        return TTC_fp

    def get_TIC_fp(self):
        TIC_fp = self.total_demand * self.H_p
        return TIC_fp

    def get_TTC_b(self):
        TTC_b = sum([retailer.get_TTC()
                    for retailer in self.retailers])
        return TTC_b

    def set_r_A(self, A):
        for idx, retailer in enumerate(self.retailers):
            retailer.A = A

    def set_r_a(self, a):
        for idx, retailer in enumerate(self.retailers):
            retailer.a = a[idx]

    def set_r_cp(self, cp):
        for idx, retailer in enumerate(self.retailers):
            retailer.cp = cp[idx]

    def set_r_val(self, A, a, cp):
        for idx, retailer in enumerate(self.retailers):
            retailer.set_retailer_val(A, a[idx], cp[idx])

    def get_m_solution(self):
        solution = []
        # for retailer in self.retailers:
        #     r_profit = retailer.get_retailer_profit()
        #     r_val = {
        #         "r_id": retailer.id,
        #         "A": retailer.A,
        #         "a": retailer.a,
        #         "cp": retailer.cp,
        #         "profit": r_profit
        #     }
        #     solution.append(r_val)
        # m_profit = self.get_m_profit()
        total_profit = self.get_total_profit()
        solution.append({
            "total_profit": total_profit
        })
        return solution

    def get_m_gen(self):
        m_gen = []
        for retailer in self.retailers:
            m_gen += [retailer.A, retailer.a, retailer.cp]
        return m_gen
