import os
import json
import math
import traceback
import logging
import random
from copy import deepcopy
from ..daos import RetailerDao, ManufacturerDao, NashGADao
from .retailer_service import RetailerService
from .manufacturer_service import ManufacturerService
from .pre_demand_service import PredictDemandModelService

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class NashGAService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.nash_ga = NashGADao()
        self.pre_demand = PredictDemandModelService()
        self.retailer_dao = RetailerDao()
        self.mft_dao = ManufacturerDao()
        self.mft_list = []
        self.nash_solution = []
        self.g_num = self.nash_ga.g_num
        self.p_size = self.nash_ga.p_size
        self.s_size = int(self.p_size * (1 - self.nash_ga.s_rate))
        self.c_size = int(self.p_size * (1 - self.nash_ga.c_rate))
        self.m_size = int(self.p_size * (1 - self.nash_ga.m_rate))
        self.generation_fitness = [0] * self.p_size
        self.is_log = 0

    def process(self, is_log):
        self.is_log = is_log
        self.create_population()
        for g_idx in range(self.g_num):
            self.selection()
            self.crossover()
            self.mutations()

        solution = [p["p"] for p in self.nash_solution]
        solution.sort()
        best_profit = solution[-1]

        return {
            "best_profit": best_profit,
            "log": self.nash_solution
        }

    def gen_random_val(self):
        while True:
            A = random.randrange(1, self.nash_ga.MAX_A)
            a_list = [random.randrange(1, self.nash_ga.MAX_a)
                      for _ in range(self.mft_dao.NUM_OF_RETAILERS)]
            material_cost = self.mft_dao.materials_cost
            p = self.mft_dao.p
            cp_list = [random.randrange(
                material_cost, p) for _ in range(self.mft_dao.NUM_OF_RETAILERS)]
            if self.pre_demand.get_total_predict(A, a_list, cp_list) < self.mft_dao.P:
                return [A, a_list, cp_list]

    def create_population(self):
        for i in range(self.p_size):
            mft = ManufacturerService()
            [A, a_list, cp_list] = self.gen_random_val()
            mft.set_r_val(A, a_list, cp_list)
            self.mft_list.append(mft)

    def evaluation(self):
        for idx, mft in enumerate(self.mft_list):
            self.generation_fitness[idx] = mft.get_nash_ga_fitness()

    def selection(self):
        # Update Fitness
        self.evaluation()

        # Get Threshold
        tmp_fitness = self.generation_fitness[:]
        tmp_fitness.sort()
        threshold = tmp_fitness[self.s_size]

        # Get best solution
        best_mft_profit = tmp_fitness[-1]
        best_mft_idx = self.generation_fitness.index(
            best_mft_profit)
        best_mft = self.mft_list[best_mft_idx]
        best_solution = best_mft.get_m_solution(self.is_log)
        self.nash_solution.append(best_solution)

        for idx, fitness in enumerate(self.generation_fitness):
            if fitness < threshold:
                transfrom_mft_idx = random.randrange(self.p_size)
                self.mft_list[idx] = deepcopy(self.mft_list[transfrom_mft_idx])

    def crossover(self):
        for _ in range(self.c_size):
            mft_L = random.randrange(self.p_size)
            mft_R = random.randrange(self.p_size)
            mft_parent = [mft_L, mft_R]

            mft_gen_L = self.mft_list[mft_L].get_m_gen()
            mft_gen_R = self.mft_list[mft_R].get_m_gen()
            gen_len = len(mft_gen_L)

            for i in range(2):
                cur_mft_id = mft_parent[i]
                cur_mft = self.mft_list[cur_mft_id]
                for j in range(gen_len):
                    sieve = [random.randrange(2) for _ in range(gen_len)]
                    not_sieve = [1 - i for i in sieve]
                    tmp_gen = [mft_gen_L[i] * sieve[i] + mft_gen_R[i]
                               * not_sieve[i] for i in range(gen_len)]
                    # [A1, a1, cp1, A2, a2, cp2, A2, a2, cp2] --> A & [a1, a2, a3] & [cp1, cp2, cp3]
                    A = tmp_gen[0]
                    a_list = []
                    for i in range(self.mft_dao.NUM_OF_RETAILERS):
                        a_list.append(tmp_gen[1 + i * 3])
                    cp_list = []
                    for i in range(self.mft_dao.NUM_OF_RETAILERS):
                        cp_list.append(tmp_gen[2 + i * 3])
                    if self.pre_demand.get_total_predict(A, a_list, cp_list) < self.mft_dao.P:
                        cur_mft.set_r_val(A, a_list, cp_list)
                        break

    def mutations(self):
        for _ in range(self.m_size):
            mut_mft_id = random.randrange(self.p_size)
            while True:
                [A, a_list, cp_list] = self.gen_random_val()
                if self.pre_demand.get_total_predict(A, a_list, cp_list) < self.mft_dao.P:
                    self.mft_list[mut_mft_id].set_r_val(A, a_list, cp_list)
                    break
