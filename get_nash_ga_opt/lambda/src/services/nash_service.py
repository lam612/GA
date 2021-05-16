import os
import json
import math
import traceback
import logging
import random
from copy import deepcopy
from ..daos import ManufacturerDao, NashDao, GADao
from .ga_service import GAService, ManufacturerService
from .pre_demand_service import PredictDemandModelService

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class NashService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.nash_dao = NashDao()
        self.ga_dao = GADao()
        self.mf_dao = ManufacturerDao()
        self.mf_service = ManufacturerService()
        self.pre_demand = PredictDemandModelService()
        self.solution = {}
        self.nash_strategy = []
        self.beta = self.nash_dao.beta

    def process(self):
        step = 0
        strategy_list = {}
        self.generate_initial_individual()
        while True:
            strategy_list[step] = self.get_cur_nash_strategy()

            self.optimal()

            # Check nash
            is_nash_eq = self.check_nash_eq()
            A, cp, a, fitness, demands, profits = best_strategy = self.nash_strategy[-1]
            if is_nash_eq:
                print("\n{}\n[*] {:^88s} [*]".format("=" *
                                                     96, "NASH EQ"))
                print("[A] {}\n[a] {}\n[S] {}\n[F] {}\n[D] {}\n[P] {}\n".format(
                    A, cp, a, fitness, demands, profits))
                print("{} - NASH  EQ {} - {}\n".format("=" * 40, step,  "=" * 40))
                return strategy_list

            elif step > 30:
                print("\n{} - NO  NASH EQ {} - {}".format("-" * 39, step,  "-" * 39))
                print("[$] Best Strategy [$]")
                print("[A] {}\n[a] {}\n[cp] {}\n[F] {}\n[D] {}\n[P] {}\n".format(
                    A, cp, a, fitness, demands, profits))
                return strategy_list

            step += 1

    def optimal(self):
        next_solution = self.calc_next_solution()
        for player_id in self.nash_dao.nash.keys():
            player_solution = next_solution[player_id]
            ga_service = GAService(player_id, player_solution)
            optimal_solution = ga_service.optimal()
            self.solution[player_id].append(optimal_solution)

    def gen_random_solution(self):
        while True:
            A = random.randrange(1, self.ga_dao.MAX_A)

            material_cost = self.mf_dao.materials_cost
            p = self.mf_dao.p
            cp_list = [random.randrange(
                material_cost, p * 0.95) for _ in range(self.mf_dao.NUM_OF_RETAILERS)]

            a_list = [random.randrange(1, self.ga_dao.MAX_a)
                      for _ in range(self.mf_dao.NUM_OF_RETAILERS)]
            if self.pre_demand.get_total_predict(A, a_list, cp_list) < self.mf_dao.P:
                strategy = [A, cp_list, a_list]
                solution = {
                    "fitness": 0,
                    "solution": strategy
                }
                return solution

    def generate_initial_individual(self):
        for player_id in self.nash_dao.nash.keys():
            self.solution[player_id] = [self.gen_random_solution()]
        self.nash_strategy.append(self.get_cur_nash_eq())

    def calc_next_solution(self):
        # Get previous solution
        pre_mf_ads, pre_mf_cp, pre_r_ads, _, _, _ = self.get_cur_nash_eq()

        # Generate next step solution
        next_solution = {}
        r_idx = -1
        for player_id in self.nash_dao.nash.keys():
            if player_id == self.nash_dao.mf_id:
                dump_cp_list = [0] * self.mf_dao.NUM_OF_RETAILERS
                # Next solution : A, cp_list, a_list*
                next_solution[player_id] = [
                    0, dump_cp_list, pre_r_ads]
            else:
                dump_r_ads = pre_r_ads[:]
                dump_r_ads[r_idx] = 0
                next_solution[player_id] = [pre_mf_ads, pre_mf_cp, dump_r_ads]

            r_idx += 1

        return next_solution

    def compare_fitness(self, nash_str_fitness, target_str_fitness):
        max_error = self.beta

        for idx, _ in enumerate(nash_str_fitness):
            error = abs(nash_str_fitness[idx] - target_str_fitness[idx])
            gama = error / target_str_fitness[idx]
            if gama > max_error:
                print("\n[!] {}\n[{}] {}".format(nash_str_fitness,
                      idx, target_str_fitness))
                print("[%] Gama : {:^2.5f} | Error : {:^2.5f} | {} | {} - {}".format(gama, max_error,
                      error, nash_str_fitness[idx], target_str_fitness[idx]))
                return idx + 10

        return 1

    def check_nash_eq(self):
        cur_nash_str = self.get_cur_nash_eq()
        self.nash_strategy.append(cur_nash_str)
        str_len = len(self.nash_strategy)
        print("{} {} {}".format("*" * 39, "START CHECK NASH EQ", "*" * 36))
        cur_str_list = self.get_cur_nash_strategy()
        self.beta *= 1.02
        print("[P] {}".format(self.nash_strategy[-2]))
        print("[C] {}".format(self.nash_strategy[-1]))

        pre_nash_strategy = self.nash_strategy[-2][3]
        cur_nash_strategy = self.nash_strategy[-1][3]

        is_nash_eq = self.compare_fitness(pre_nash_strategy, cur_nash_strategy)

        if is_nash_eq > 1:
            print("{} NO  EQ [{}] {}\n".format(
                "*" * 42, is_nash_eq - 9, "*" * 42))
            return 0

        return 1

    def get_cur_nash_strategy(self):
        strategy = []
        for player_id in self.nash_dao.nash.keys():
            strategy.append(self.solution[player_id][-1])
        return strategy

    def get_cur_nash_eq(self):
        pre_mf_ads, pre_mf_cp, pre_r_ads = 0, [], []
        r_idx = -1
        for player_id in self.nash_dao.nash.keys():
            player_pre_solution = self.solution[player_id][-1]
            if player_id == self.nash_dao.mf_id:
                pre_mf_ads, pre_mf_cp = player_pre_solution["solution"][0], player_pre_solution["solution"][1]
            else:
                pre_r_ads.append(player_pre_solution["solution"][2][r_idx])

            r_idx += 1

        self.mf_service.set_m_val(pre_mf_ads, pre_mf_cp, pre_r_ads)
        fitness_list = []
        for weight in self.nash_dao.nash.values():
            player_fitness = self.mf_service.calc_fitness(weight)
            fitness_list.append(player_fitness)
        retailers_demand = self.mf_service.get_retailers_demand_list()
        retailers_profit = self.mf_service.get_model_profit_list()
        return [pre_mf_ads, pre_mf_cp, pre_r_ads, fitness_list, retailers_demand, retailers_profit]
