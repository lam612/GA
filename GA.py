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

    def calc_deman(self, a, A):
        D = 0
        for i in range(len(a) - 1):
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
            A = self.H
            a = [self.H, self.H, self.H, self.H, self.H]
            n_j = []
            while self.calc_deman(a, A) > config.P:
                A = random.randrange(1, self.H)
                for j in range(len(a)):
                    a[j] = random.randrange(1, self.H)
            for j in range(len(config.M)):
                n_j.append(random.randrange(2, 20))
            if self.calc_deman(a, A) < config.P:
                x = 1
            else:
                x = 0
            manufacturer = Manufacturer(A, n_j, x)
            for j in range(len(a)):
                retainer = Retailer(j, a[j])
                retainer.calculator_b()
                manufacturer.retailers.append(retainer)
            manufacturer.calc_C()
            self.manufacturers.append(manufacturer)

    def evaluation(self):
        for i in range(self.population):
            profit = 0
            profit += self.manufacturers[i].get_mf_profit()
            for j in range(len(config.M)):
                e_A = self.manufacturers[i].e_A
                A = self.manufacturers[i].A
                profit += self.manufacturers[i].retailers[j].get_profit(
                    A, e_A)
            self.profit_list[i] = profit

    def selection(self):
        temp = self.profit_list[:]
        temp.sort()
        threshold = temp[int((1-self.p_selection) * self.population)]
        for i in range(self.population):
            if self.profit_list[i] < threshold:
                k = random.randrange(self.population)
                self.manufacturers[i] = deepcopy(self.manufacturers[k])

    def crossover(self):
        for i in range(int(self.population * self.p_crossover)):
            mf_L = random.randrange(self.population)
            mf_R = random.randrange(self.population)

            # crossover n_j
            for j in range(len(config.H_r)):
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
            mf_LR_chomo = np.matrix([mf_L_chomo, mf_R_chomo])

            for i in range(2):
                new_mf_chomo = []
                for j in range(len(config.H_r)):
                    mf_LR_chomo = np.matrix([mf_L_chomo, mf_R_chomo])
                    sieve = np.random.randint(2, size=6)
                    not_sieve = sieve ^ 1
                    tmp_chomo = [mf_L_chomo[i] * sieve[i] +
                                 mf_R_chomo[i] * not_sieve[i] for i in range(6)]
                    if self.calc_deman(tmp_chomo[1:], tmp_chomo[0]) < config.P:
                        new_mf_chomo = tmp_chomo
                        break
                self.manufacturers[new_mf_list[i]
                                   ].A = new_mf_chomo[0]
                self._set_rts_ads(new_mf_list[i], new_mf_chomo[1:])

            self.manufacturers[mf_L].calc_C()
            self.manufacturers[mf_R].calc_C()

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
            best_mf.get_model_profit(), best_mf.A, best_mf.C, best_mf.get_model_demand(), best_mf.get_mf_profit()), end='')

        # Material cycle
        for j in best_mf.n:
            print(' | {:>4d}'.format(j), end='')
        for idx, val in enumerate(best_mf.retailers):
            print(' | {:>8.0f} | {:>11.0f}'.format(
                val.a, best_mf.get_rt_profit(idx)), end='')
        print('')
