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
        self.mf_dao = ManufacturerDao()
        self.S_p = self.mf_dao.S_p
        self.T_p = self.mf_dao.T_p
        self.H_p = self.mf_dao.H_p
        self.p = self.mf_dao.p
        self.M_p = self.mf_dao.M_p
        self.M_s = self.mf_dao.M_s
        self.P = self.mf_dao.P
        self.C = self.mf_dao.C
        self.CT_r = []
        self.materials = self.mf_dao.materials
        self.NUM_OF_MATERIALS = self.mf_dao.NUM_OF_MATERIALS
        self.NUM_OF_RETAILERS = self.mf_dao.NUM_OF_RETAILERS
        self.r_ids = self.mf_dao.r_ids
        self.retailers = self.get_retailers()
        self.CT_fp = 0
        self.total_demand = 0
        self.A = 0
        self.fitness = 0

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

    def get_retailers_demand_list(self):
        r_demand_list = []
        for retailer in self.retailers:
            r_demand_list.append(retailer.get_retailer_demand())
        return r_demand_list

    def set_total_demand(self):
        self.total_demand = sum(
            [retailer.get_retailer_demand() for retailer in self.retailers])

    def get_r_profit(self, r_id):
        return self.get_retailer(r_id).get_retailer_profit()

    def get_retailers_profit_list(self):
        r_demand_list = []
        for retailer in self.retailers:
            r_demand_list.append(retailer.get_retailer_profit())
        return r_demand_list

    def get_model_profit_list(self):
        return [int(self.get_m_profit())] + self.get_retailers_profit_list()

    def get_total_r_profit(self):
        return sum([retailer.get_retailer_profit() for retailer in self.retailers])

    def calc_fitness(self, weight_list):
        if abs(sum(weight_list) - 1) > 0.01:
            print("[Error] {} - {}".format(weight_list, sum(weight_list)))
        mf_fitness = self.get_m_profit() * weight_list[0]
        rtl_fitness = sum([weight_list[idx + 1] *
                          retailer.get_retailer_profit() for idx, retailer in enumerate(self.retailers)])
        self.fitness = int(mf_fitness + rtl_fitness)
        return self.fitness

    def get_m_profit(self):
        self.set_total_demand()
        if self.total_demand == 0:
            return 0
        NP_M = self.get_TR_M() - self.get_TC_M()
        return NP_M

    def get_total_profit(self):
        return self.get_total_r_profit() + self.get_m_profit()

    def get_total_m_ads(self):
        total_m_ads = self.total_demand * self.A
        return total_m_ads

    def get_TR_M(self):
        TR_M = sum([retailer.get_m_debt() for retailer in self.retailers])
        return round(TR_M, 2)

    def get_TC_M(self):
        TC_M = self.get_TDC_M() + self.get_TIDC_M()
        return round(TC_M, 2)

    def get_TDC_M(self):
        material_cost = self.mf_dao.materials_cost
        direct_cost_per_unit = material_cost + self.M_p + self.M_s
        TDC_M = self.total_demand * direct_cost_per_unit * self.mf_dao.p_rate
        return round(TDC_M, 2)

    def get_TIDC_M(self):
        TIDC_M = self.get_TIC() + self.get_TTC() + self.get_total_m_ads()
        return round(TIDC_M, 2)

    def get_TIC(self):
        TIC = self.get_TIC_r() + self.get_TIC_fp()
        return round(TIC, 2)

    def get_TTC(self):
        TTC = self.get_TTC_r() + self.get_TTC_fp() + self.get_TTC_b()
        return round(TTC, 2)

    def get_TTC_r(self):
        TTC_r = 0
        self.CT_r = []
        for material in self.materials.values():
            T_fee = self.total_demand * \
                material["M"] * material["T_r"] * self.mf_dao.p_rate
            CT_r = round(math.sqrt(material["S_r"] / T_fee), 4)
            self.CT_r.append(CT_r)
            TTC_r += material["S_r"] / CT_r + T_fee * CT_r
        return round(TTC_r, 2)

    def get_TIC_r(self):
        TIC = 0
        for material in self.materials.values():
            TIC += (material["n"] + 1) * self.total_demand * \
                material["M"] * material["H_r"] / 2 * self.mf_dao.p_rate
        return round(TIC, 2)

    def get_TTC_fp(self):
        T_fee = self.total_demand * self.T_p * (1 + self.mf_dao.L_factory)
        self.CT_fp = math.sqrt(self.S_p / T_fee)
        TTC_fp = round(self.S_p / self.CT_fp + T_fee * self.CT_fp, 2)
        return TTC_fp

    def get_TIC_fp(self):
        TIC_fp = round(self.total_demand * self.H_p *
                       (1 + self.mf_dao.L_factory), 2)
        return TIC_fp

    def get_TTC_b(self):
        TTC_b = sum([retailer.get_TTC()
                    for retailer in self.retailers])
        return round(TTC_b, 2)

    def set_r_A(self, A):
        for idx, retailer in enumerate(self.retailers):
            retailer.A = A

    def set_r_a(self, a):
        for idx, retailer in enumerate(self.retailers):
            retailer.a = a[idx]

    def set_r_cp(self, cp):
        for idx, retailer in enumerate(self.retailers):
            retailer.cp = cp[idx]

    def set_m_val(self, A, cp, a):
        self.A = A
        for idx, retailer in enumerate(self.retailers):
            retailer.set_retailer_val(A, cp[idx], a[idx])

    def get_m_solution(self):

        A, cp_list, a_list = self.A, [], []
        r_demand = []
        for retailer in self.retailers:
            cp_list.append(retailer.cp)
            a_list.append(retailer.a)
            r_demand.append(retailer.get_retailer_demand())

        return {
            "fitness": self.fitness,
            "solution": [A, cp_list, a_list],
            "demand": self.total_demand,
            "r_demand": r_demand
        }

    def get_m_gen(self):
        m_gen = [self.A]
        for retailer in self.retailers:
            m_gen += [retailer.a, retailer.cp]
        return m_gen

    def get_VMI_CT(self):
        CT_b = [retailer.CT_fp for retailer in self.retailers]
        CT_list = {
            "CT_r": self.CT_r,
            "CT_fp": self.CT_fp,
            "CT_b": CT_b
        }
        return CT_list

    def get_m_cost_list(self):
        cost_list = {
            "TTC_r": self.get_TTC_r(),
            "TTC_b": self.get_TTC_b(),
            "TTC_fp": self.get_TTC_fp(),
            "TIC_r": self.get_TIC_r(),
            "TIC_fp": self.get_TIC_fp(),
            "TTC": self.get_TTC(),
            "TIC": self.get_TIC(),
            "TAdC": self.get_total_m_ads(),
            "TIDC_M": self.get_TIDC_M(),
            "TDC_M": self.get_TDC_M(),
            "TC_M": self.get_TC_M(),
            "TR_M": self.get_TR_M(),
        }
        return cost_list
