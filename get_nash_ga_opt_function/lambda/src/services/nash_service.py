import os
import json
import math
import traceback
import logging
import random
from copy import deepcopy
from ..daos import ManufacturerDao, NashDao
from .ga_service import GAService, ManufacturerService
from .pre_demand_service import PredictDemandModelService
from .vmi_val_service import VMIValService
from ..constants import JobStatus
from ..constants import CommonConfig

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class NashService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.vmi_val_service = VMIValService()
        self.solution = {}
        self.nash_strategy = []
        self.strategy_list = {}

    def init_dao(self):
        self.nash_dao = NashDao()
        self.mf_dao = ManufacturerDao()
        self.mf_service = ManufacturerService()
        self.pre_demand = PredictDemandModelService()
        self.beta = self.nash_dao.beta

    def process(self, vmi_id, context):
        # Read VMI Variable from DynamoDB
        self.vmi_val_service.get_vmi_val_by_id(vmi_id)
        self.vmi_val_service.update_item_status(vmi_id, JobStatus.RUNNING)
        self.init_dao()

        step = 0
        self.generate_initial_individual()
        while True:
            self.strategy_list[step] = self.get_cur_nash_strategy()

            self.optimal()

            # Check nash
            is_nash_eq = self.check_nash_eq()

            if is_nash_eq or step > CommonConfig.MAX_NASH_GA_LOOP:

                responce = self.get_nash_ga_response(
                    vmi_id, context, is_nash_eq, step)
                return responce

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
            A = random.randrange(1, CommonConfig.MAX_A)

            material_cost = self.mf_dao.materials_cost
            p = self.mf_dao.p
            cp_list = [random.randrange(
                int(material_cost), int(p * 0.95)) for _ in range(self.mf_dao.NUM_OF_RETAILERS)]

            a_list = [random.randrange(1, CommonConfig.MAX_a)
                      for _ in range(self.mf_dao.NUM_OF_RETAILERS)]
            if self.pre_demand.get_total_predict(A, a_list, cp_list) < self.mf_dao.P:
                strategy = [A, cp_list, a_list]
                solution = {
                    "fitness": 0,
                    "solution": strategy
                }
                return solution

    def get_nash_ga_response(self, vmi_id, context, is_nash_eq, step):
        cur_strategy = self.nash_strategy[-1]
        A, cp, a, fitness, demand, profit = cur_strategy["A"], cur_strategy["cp"], cur_strategy[
            "a"], cur_strategy["fitness"], cur_strategy["demand"], cur_strategy["profit"]

        if is_nash_eq:
            print("\n{}\n[*] {:^88s} [*]".format("=" *
                                                 96, "NASH EQ"))
            nash_strategy = self.nash_strategy[-1]
            # self.vmi_val_service.update_item(
            #     vmi_id, JobStatus.SUCCEED, json.dumps(nash_strategy), json.dumps(self.nash_strategy))

        else:
            print("\n{} - NO  NASH EQ {} - {}".format("-" * 39, step,  "-" * 39))
            fitness_list = [sum(strategy["fitness"])
                            for strategy in self.nash_strategy]
            nash_strategy_id = fitness_list.index(max(fitness_list))
            nash_strategy = self.nash_strategy[nash_strategy_id]
            # self.vmi_val_service.update_item(
            #     vmi_id, JobStatus.FAILED, json.dumps(nash_strategy), json.dumps(self.nash_strategy))

        print("[A] {}\n[a] {}\n[S] {}\n[F] {}\n[D] {}\n[P] {}\n".format(
            A, cp, a, fitness, demand, profit))
        process_time_secs = round(
            900 - context.get_remaining_time_in_millis()/1000, 2)
        print("[EVENT] {} {}".format(vmi_id, process_time_secs / 1000 / 60))

        responce = {
            "process": process_time_secs,
            "nash_strategy": nash_strategy,
            "nash_ga_log": self.nash_strategy
        }

        return responce

    def generate_initial_individual(self):
        for player_id in self.nash_dao.nash.keys():
            self.solution[player_id] = [self.gen_random_solution()]
        self.nash_strategy.append(self.get_cur_nash_eq())

    def calc_next_solution(self):
        # Get previous solution
        cur_nash_strategy = self.get_cur_nash_eq()
        pre_mf_ads, pre_mf_cp, pre_r_ads = cur_nash_strategy[
            "A"], cur_nash_strategy["cp"], cur_nash_strategy["a"]

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
            if nash_str_fitness[idx] * target_str_fitness[idx] < 0:
                return idx + 10
            error = abs(nash_str_fitness[idx] - target_str_fitness[idx])
            gama = error / abs(target_str_fitness[idx])
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

        pre_nash_strategy = self.nash_strategy[-2]["fitness"]
        cur_nash_strategy = self.nash_strategy[-1]["fitness"]

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
        mf_cost_list = self.mf_service.get_m_cost_list()
        mf_CT_list = self.mf_service.get_VMI_CT()

        cur_nash = {
            "A": pre_mf_ads,
            "cp": pre_mf_cp,
            "a": pre_r_ads,
            "CT": mf_CT_list,
            "cost": mf_cost_list,
            "fitness": fitness_list,
            "demand": retailers_demand,
            "profit": retailers_profit
        }
        # return [pre_mf_ads, pre_mf_cp, pre_r_ads, fitness_list, retailers_demand, retailers_profit]
        return cur_nash
