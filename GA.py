# -*- coding: utf-8 -*-
import numpy as np
from Manufacturer import Manufacturer
from Retailer import Retailer
import config
import random
from copy import deepcopy


class GA:
    def __init__(self, population):
        self.manufacturers = []
        self.population = population
        self.p_selection = 0.8
        self.p_crossover = 0.2
        self.p_mutation = 0.3
        self.profit_list = [0] * self.population
        self.H = 400000
        self.optimal = {}
        self.populations_profit = 0

    def calc_deman(self, a, A):
        D = 0
        for i in range(config.R_len):
            D += config.K[i] * pow(a[i], config.e_a[i]) * pow(A, config.e_A) / \
                pow(config.p[i] / config.cp[i], config.e_p[i])
        return D

    def _get_demand(self, mf_id):
        D = 0
        for i in range(len(config.K)):
            cur_retailer = self.manufacturers[mf_id].retailers[i]
            A = self.manufacturers[mf_id].A
            e_A = self.manufacturers[mf_id].e_A
            D += cur_retailer.get_demand(A, e_A)
        return D

    def _get_rts_ads(self, mf_id):
        return [rt.a for rt in self.manufacturers[mf_id].retailers]

    def _set_rts_ads(self, mf_id, ads):
        for idx, retailer in enumerate(self.manufacturers[mf_id].retailers):
            retailer.a = ads[idx]

    def create(self):
        for i in range(self.population):
            while True:
                A = random.randrange(1, self.H)
                a = random.sample(range(self.H), config.R_len)
                if (self.calc_deman(a, A) < config.P):
                    break

            n_j = random.sample(range(2, 21), config.M_len)
            x = 1 if self.calc_deman(a, A) == config.P else 0
            manufacturer = Manufacturer(A, n_j, x)
            for j in range(len(a)):
                retainer = Retailer(j, a[j])
                manufacturer.retailers.append(retainer)
            manufacturer.calc_C()
            self.manufacturers.append(manufacturer)

    def evaluation(self):
        for i in range(self.population):
            self.profit_list[i] = self.manufacturers[i].get_total_profit()
        self.populations_profit = sum(self.profit_list)

    def selection(self):
        cur_profit = self.populations_profit
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
        crossed_profit = self.populations_profit
        bcolors = config.bcolors.HEADER if cur_profit > crossed_profit else config.bcolors.OKCYAN
        print("[E] {:<15.2f} [C] {}{:<15.2f}{}".format(cur_profit, bcolors,
                                                       crossed_profit, config.bcolors.ENDC), end=' ')

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
            mf_L_chomo = self._get_rts_ads(
                mf_L)
            mf_L_chomo.append(self.manufacturers[mf_L].A)
            mf_R_chomo = self._get_rts_ads(
                mf_R)
            mf_R_chomo.append(self.manufacturers[mf_R].A)
            mf_LR_chomo = [mf_L_chomo, mf_R_chomo]

            for i in range(2):
                new_mf_chomo = mf_LR_chomo[i]
                cur_mf_idx = new_mf_list[i]
                cur_mf = self.manufacturers[cur_mf_idx]
                for j in range(config.R_len * 2):
                    sieve = np.random.randint(2, size=6)
                    not_sieve = sieve ^ 1
                    tmp_chomo = [mf_L_chomo[i] * sieve[i] +
                                 mf_R_chomo[i] * not_sieve[i] for i in range(6)]
                    tmp_mf = Manufacturer(
                        tmp_chomo[0], cur_mf.n, cur_mf.x)
                    for j in range(config.R_len):
                        retainer = Retailer(j, tmp_chomo[j + 1])
                        tmp_mf.retailers.append(retainer)
                    tmp_mf.calc_C()

                    if self.calc_deman(tmp_chomo[1:], tmp_chomo[0]) < config.P and tmp_mf.get_total_profit() > cur_mf.get_total_profit():
                        self.manufacturers[cur_mf_idx] = deepcopy(tmp_mf)
                        break
        self.evaluation()

        crossed_profit = self.populations_profit
        bcolors = config.bcolors.HEADER if cur_profit > crossed_profit else config.bcolors.OKCYAN
        print("[C] {}{:<15.2f}{}".format(bcolors,
                                         crossed_profit, config.bcolors.ENDC))

    def mutation(self):
        for i in range(int(self.population*self.p_mutation)):
            index = random.randrange(self.population)
            # mutation A
            while self._get_demand(index) > config.P:
                self.manufacturers[index].A = random.randrange(1, self.H)

            # mutation a
            while self._get_demand(index) > config.P:
                for j in range(len(config.e_a)):
                    if random.randrange(2) == 1:
                        self.manufacturers[index].retailers[j].a = random.randrange(
                            1, self.H)

            # mutation n
            for j in range(len(config.M)):
                if random.randrange(2) == 1:
                    self.manufacturers[index].n[j] = random.randint(2, 20)
            self.manufacturers[index].calc_C()

    def get_best_mf(self):
        best_mf_id = self.profit_list.index(max(self.profit_list))
        return self.manufacturers[best_mf_id]

    def show_optimal(self):
        best_mf = self.get_best_mf()
        print('{:>12.0f} | {:>8d} | {:>2.4f} | {:>8.0f} | {:>9.0f}'.format(
            best_mf.get_total_profit(), best_mf.A, best_mf.C, best_mf.get_model_demand(), best_mf.get_mf_profit()), end='')

        # Material cycle
        for j in best_mf.n:
            print(' | {:>4d}'.format(j), end='')
        for idx, val in enumerate(best_mf.retailers):
            print(' | {:>8.0f} | {:>11.0f}'.format(
                val.a, best_mf.get_rt_profit(idx)), end='')
        print('')
