import os
import json
import math
import traceback
import logging
import random
from copy import deepcopy
from ..daos import RetailerDao, ManufacturerDao, NashDao
from .manufacturer_service import ManufacturerService
from .pre_demand_service import PredictDemandModelService
from ..constants import CommonConfig

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class GAService:
    def __init__(self, player_id, strategy):
        self.logger = logging.getLogger(__name__)
        self.nash_dao = NashDao()
        self.pre_demand = PredictDemandModelService()
        self.retailer_dao = RetailerDao()
        self.mf_dao = ManufacturerDao()
        self.mf_list = []
        self.nash_solution = []
        self.s_size = int(CommonConfig.POPULATION_NUMBER *
                          (1 - CommonConfig.SELECTION_RATE))
        self.c_size = int(CommonConfig.POPULATION_NUMBER *
                          (1 - CommonConfig.CROSSOVER_RATE))
        self.m_size = int(CommonConfig.POPULATION_NUMBER *
                          (1 - CommonConfig.MUTATION_RATE))
        self.generation_fitness = [0] * CommonConfig.POPULATION_NUMBER
        self.player_id = player_id
        self.player_idx = list(self.nash_dao.nash.keys()).index(player_id) - 1
        self.pre_m_ads = strategy[0]
        self.pre_m_cp_list = strategy[1]
        self.pre_r_ads_list = strategy[2]

    def optimal(self):
        self.create_population()
        for _ in range(CommonConfig.GENERATION_NUMBER):
            self.selection()
            self.crossover()
            self.mutations()

        fitness_list = [p["fitness"] for p in self.nash_solution]
        tmp_fitness = fitness_list[:]
        tmp_fitness.sort()
        best_fitness = tmp_fitness[-1]
        best_fitness_idx = fitness_list.index(best_fitness)

        best_solution = self.nash_solution[best_fitness_idx]
        return best_solution

    def gen_random_val(self):
        material_cost = self.mf_dao.materials_cost
        p = self.mf_dao.p
        id = 1
        while True:
            a_list = self.pre_r_ads_list[:]
            cp_list = self.pre_m_cp_list[:]

            # Random retailer variables
            if self.player_id != self.nash_dao.mf_id:
                A = self.pre_m_ads
                tmp_r_ads = random.randrange(1, CommonConfig.MAX_a)
                a_list[self.player_idx] = tmp_r_ads

            # Random manufacturer variables
            else:
                A = random.randrange(1, CommonConfig.MAX_A)
                cp_list = [random.randrange(
                    int(material_cost), int(p * 0.95)) for _ in range(self.mf_dao.NUM_OF_RETAILERS)]

            if self.pre_demand.get_total_predict(A, a_list, cp_list) < self.mf_dao.P:
                return [A, a_list, cp_list]
            id += 1

    def create_population(self):
        for i in range(CommonConfig.POPULATION_NUMBER):
            mf = ManufacturerService()
            [A, a_list, cp_list] = self.gen_random_val()
            mf.set_m_val(A, cp_list, a_list)
            self.mf_list.append(mf)

    def evaluation(self):
        for idx, mf in enumerate(self.mf_list):
            weight_list = self.nash_dao.nash[self.player_id]
            self.generation_fitness[idx] = mf.calc_fitness(weight_list)

    def selection(self):
        # Update Fitness
        self.evaluation()

        # Get Threshold
        tmp_fitness = self.generation_fitness[:]
        tmp_fitness.sort()
        threshold = tmp_fitness[self.s_size]

        # Get best solution
        best_mf_profit = tmp_fitness[-1]
        best_mf_idx = self.generation_fitness.index(
            best_mf_profit)
        best_mf = self.mf_list[best_mf_idx]
        best_solution = best_mf.get_m_solution()
        self.nash_solution.append(best_solution)

        for idx, fitness in enumerate(self.generation_fitness):
            if fitness < threshold:
                transfrom_mf_idx = random.randrange(
                    CommonConfig.POPULATION_NUMBER)
                self.mf_list[idx] = deepcopy(self.mf_list[transfrom_mf_idx])

    def crossover(self):
        for _ in range(self.c_size):
            mf_L = random.randrange(CommonConfig.POPULATION_NUMBER)
            mf_R = random.randrange(CommonConfig.POPULATION_NUMBER)
            mf_parent = [mf_L, mf_R]

            mf_gen_L = self.mf_list[mf_L].get_m_gen()
            mf_gen_R = self.mf_list[mf_R].get_m_gen()
            gen_len = len(mf_gen_L)

            for n in range(2):
                cur_mf_id = mf_parent[n]
                cur_mf = self.mf_list[cur_mf_id]
                for j in range(gen_len):
                    sieve = [random.randrange(2) for _ in range(gen_len)]
                    not_sieve = [1 - i for i in sieve]
                    tmp_gen = [mf_gen_L[i] * sieve[i] + mf_gen_R[i]
                               * not_sieve[i] for i in range(gen_len)]
                    # [A1, a1, cp1, a2, cp2, a2, cp2] --> A & [a1, a2, a3] & [cp1, cp2, cp3]
                    A = tmp_gen[0]
                    a_list = []
                    for i in range(self.mf_dao.NUM_OF_RETAILERS):
                        a_list.append(tmp_gen[1 + i * 2])
                    cp_list = []
                    for i in range(self.mf_dao.NUM_OF_RETAILERS):
                        cp_list.append(tmp_gen[2 + i * 2])

                    if self.pre_demand.get_total_predict(A, a_list, cp_list) < self.mf_dao.P:
                        cur_mf.set_m_val(A, cp_list, a_list)
                        break

    def mutations(self):
        for _ in range(self.m_size):
            mut_mf_id = random.randrange(CommonConfig.POPULATION_NUMBER)
            while True:
                [A, a_list, cp_list] = self.gen_random_val()
                if self.pre_demand.get_total_predict(A, a_list, cp_list) < self.mf_dao.P:
                    cur_mf = self.mf_list[mut_mf_id]
                    cur_mf.set_m_val(A, cp_list, a_list)
                    break
