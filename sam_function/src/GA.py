# -*- coding: utf-8 -*-
from Retailer import Retailer
from Manufacturer import Manufacturer
from dotenv import load_dotenv
from copy import deepcopy
import numpy as np
import sys
import os
import json
import config
import random
import sys
from utils.common import LRModel

load_dotenv()


class GA:
    def __init__(self, pl_size=1000, selection_rate=0.8, crossover_rate=0.8, mutation_rate=0.3):
        self.manufacturers = []
        self.population = pl_size
        self.p_selection = selection_rate
        self.p_crossover = crossover_rate
        self.p_mutation = mutation_rate
        self.profit_list = [0] * self.population
        self.max_a = config.MAX_A
        self.max_cp = config.p
        self.min_cp = config.MIN_cp
        self.p = config.p
        self.rel_number = config.R_len
        self.optimal = {}
        self.populations_profit = 0
        self.model_val = LRModel()

    def _get_rts_variable(self, mf_id):
        return [rt.a for rt in self.manufacturers[mf_id].retailers] + [rt.cp for rt in self.manufacturers[mf_id].retailers]

    def _set_rts_variable(self, mf_id, ads):
        for idx, retailer in enumerate(self.manufacturers[mf_id].retailers):
            retailer.a = ads[idx]

    def _set_rts_sell_price(self, mf_id, sell_price):
        for idx, retailer in enumerate(self.manufacturers[mf_id].retailers):
            retailer.p = ads[idx]

    def create(self):
        for i in range(self.population):
            while True:
                A = random.randrange(1, self.max_a)
                a = random.sample(range(self.max_a), self.rel_number)
                cp = [random.randrange(
                    self.min_cp, self.max_cp) for _ in range(self.rel_number)]
                if (self.model_val.get_total_predict_value(A, a, self.p) < config.P):
                    break
            n_j = random.sample(range(2, 8), config.M_len)
            x = 1 if self.model_val.get_total_predict_value(
                A, a, self.p) == config.P else 0
            manufacturer = Manufacturer(A, n_j, x)
            for j in range(len(a)):
                retailer = Retailer(j, a[j], cp[j])
                manufacturer.retailers.append(retailer)
            manufacturer.calc_C()
            self.manufacturers.append(manufacturer)
        self.evaluation()

    def evaluation(self):
        for i in range(self.population):
            self.profit_list[i] = self.manufacturers[i].get_total_profit()
        self.populations_profit = sum(self.profit_list)

    def selection(self):
        cur_profit = self.populations_profit / self.population
        temp = self.profit_list[:]
        temp.sort()
        threshold = temp[int((1 - self.p_selection) * self.population)]
        threshold_idx = self.profit_list.index(threshold)
        good_individual_ids = [threshold_idx]
        for idx, i in enumerate(range(self.population)):
            if self.profit_list[idx] < threshold:
                k = good_individual_ids[
                    random.randrange(0, len(good_individual_ids))]
                self.manufacturers[idx] = deepcopy(self.manufacturers[k])
            else:
                good_individual_ids.append(idx)
        self.evaluation()
        # crossed_profit = self.populations_profit / self.population
        # bcolors = config.bcolors.HEADER if cur_profit > crossed_profit else config.bcolors.OKCYAN
        # print("[E] {:<15.2f} [C] {}{:<15.2f}{}".format(cur_profit, bcolors,
        #                                                crossed_profit, config.bcolors.ENDC), end=' ')

    def crossover(self):
        cur_profit = self.populations_profit

        for i in range(int(self.population * self.p_crossover)):
            mf_L = random.randrange(self.population)
            mf_R = random.randrange(self.population)

            # crossover n_j
            for j in range(config.M_len):
                if random.randrange(2) == 1:
                    self.manufacturers[mf_L].n[j], self.manufacturers[mf_R].n[
                        j] = self.manufacturers[mf_R].n[j], self.manufacturers[mf_L].n[j]

            new_mf_list = [mf_L, mf_R]
            mf_L_chomo = self._get_rts_variable(
                mf_L)
            mf_L_chomo.append(self.manufacturers[mf_L].A)
            mf_R_chomo = self._get_rts_variable(
                mf_R)
            mf_R_chomo.append(self.manufacturers[mf_R].A)
            mf_LR_chomo = [mf_L_chomo, mf_R_chomo]
            rel_variable_len = self.rel_number * 2

            for i in range(2):
                new_mf_chomo = mf_LR_chomo[i]
                cur_mf_idx = new_mf_list[i]
                cur_mf = self.manufacturers[cur_mf_idx]
                for j in range(rel_variable_len):
                    sieve = np.random.randint(2, size=rel_variable_len + 1)
                    not_sieve = sieve ^ 1
                    tmp_chomo = [mf_L_chomo[i] * sieve[i] +
                                 mf_R_chomo[i] * not_sieve[i] for i in range(rel_variable_len + 1)]
                    tmp_mf = Manufacturer(
                        tmp_chomo[-1], cur_mf.n, cur_mf.x)
                    for j in range(self.rel_number):
                        retainer = Retailer(
                            j, tmp_chomo[j], tmp_chomo[j + self.rel_number])
                        tmp_mf.retailers.append(retainer)
                    tmp_mf.calc_C()
                    A, tmp_ads_list = tmp_chomo[-1], tmp_chomo[0:
                                                               self.rel_number + 1]
                    if self.model_val.get_total_predict_value(A, tmp_ads_list, self.p) < config.P and tmp_mf.get_total_profit() > cur_mf.get_total_profit():
                        self.manufacturers[cur_mf_idx] = deepcopy(tmp_mf)
                        break

        self.evaluation()
        # crossed_profit = self.populations_profit
        # bcolors = config.bcolors.HEADER if cur_profit > crossed_profit else config.bcolors.OKCYAN
        # print("[C] {}{:<15.2f}{}".format(bcolors,
        #                                  crossed_profit, config.bcolors.ENDC))

    def mutation(self):
        for i in range(int(self.population*self.p_mutation)):
            index = random.randrange(self.population)
            # mutation A
            while self.manufacturers[index].get_total_demand() > config.P:
                self.manufacturers[index].A = random.randrange(1, self.max_a)

            # mutation a
            while self.manufacturers[index].get_total_demand() > config.P:
                for j in range(len(config.e_a)):
                    if random.randrange(2) == 1:
                        self.manufacturers[index].retailers[j].a = random.randrange(
                            1, self.max_a)

            # mutation n
            for j in range(len(config.M)):
                if random.randrange(2) == 1:
                    self.manufacturers[index].n[j] = random.randint(2, 8)
            self.manufacturers[index].calc_C()

    def get_best_mf(self):
        best_mf_id = self.profit_list.index(max(self.profit_list))
        return self.manufacturers[best_mf_id]

    def show_optimal(self):
        best_mf = self.get_best_mf()
        print('{:>12.0f} | {:>8.0f} | {:>2.4f} | {:>8.0f} | {:>9.0f}'.format(
            best_mf.get_total_profit(), best_mf.A, best_mf.C, best_mf.get_total_demand(), best_mf.get_mf_profit()), end='')

        # Material cycle
        for j in best_mf.n:
            print(' | {:>4d}'.format(j), end='')
        for idx, val in enumerate(best_mf.retailers):
            print(' | {:>8.0f} | {:>11.0f}'.format(
                val.a, best_mf.get_rt_profit(idx)), end='')
        print('')
