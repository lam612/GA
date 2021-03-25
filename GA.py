# -*- coding: utf-8 -*-
import numpy as np
from Manufacturer import Manufacturer
from Retailer import Retailer
import config
import random
from copy import deepcopy


class GA:
    def __init__(self, n):
        self.manufacturers = []
        self.n = n
        self.p_selection = 0.8
        self.p_crossover = 0.2
        self.p_mutation = 0.3
        self.profit_list = [0] * self.n
        self.H = 400000
        self.optimal = {}

    def calculator_mono_deman(self, a, A, e_a, e_A, K):
        D = 0
        for i in range(len(a)):
            D += K[i] * pow(a[i], e_a[i]) * pow(A, e_A)
        return D

    def get_crossover_mono_demand(self, t):
        D = 0
        for i in range(len(config.e_a)):
            a_i = self.manufacturers[t].retailers[i].a
            e_ai = self.manufacturers[t].retailers[i].e_a
            A = self.manufacturers[t].A
            e_A = self.manufacturers[t].e_A
            D += config.K[i] * pow(a_i, e_ai) * pow(A, e_A)
        return D

    def create(self):
        for i in range(self.n):
            A = self.H
            a = [self.H, self.H, self.H, self.H, self.H]
            n_j = []
            while self.calculator_mono_deman(a, A, config.e_a, config.e_A, config.K) > config.P:
                A = random.randrange(1, self.H)
                for j in range(len(a)):
                    a[j] = random.randrange(1, self.H)
            for j in range(len(config.M)):
                n_j.append(random.randrange(2, 20))
            if self.calculator_mono_deman(a, A, config.e_a, config.e_A, config.K) < config.P:
                x = 1
            else:
                x = 0
            manufacturer = Manufacturer(config.cm, config.cr, config.H_p, config.H_r,
                                        config.M, config.P, config.S_p, config.S_r, A, config.e_A, n_j, x)
            for j in range(len(a)):
                retainer = Retailer(config.e_a[j], config.K[j], config.phi[j], config.uc[j], config.cp[j],
                                    config.H_b[j], config.L_b[j], config.S_b[j], config.p[j], config.e_p[j], a[j])
                retainer.calculator_b()
                manufacturer.retailers.append(retainer)
            manufacturer.caculator_C()
            self.manufacturers.append(manufacturer)

    def evaluation(self):
        for i in range(self.n):
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
        threshold = temp[int((1-self.p_selection) * self.n)]
        for i in range(self.n):
            if self.profit_list[i] < threshold:
                k = random.randrange(self.n)
                self.manufacturers[i] = deepcopy(self.manufacturers[k])

    def crossover(self):
        for i in range(int(self.n * self.p_crossover)):
            father = random.randrange(self.n)
            mother = random.randrange(self.n)

            # crossover A
            if random.randrange(2) == 1:
                self.manufacturers[father].A, self.manufacturers[
                    mother].A = self.manufacturers[mother].A, self.manufacturers[father].A
                if (self.get_crossover_mono_demand(father) > config.P or self.get_crossover_mono_demand(mother) > config.P):
                    self.manufacturers[father].A, self.manufacturers[
                        mother].A = self.manufacturers[mother].A, self.manufacturers[father].A

            # crossover a
            for j in range(len(config.e_a)):
                if random.randrange(2) == 1:
                    self.manufacturers[father].retailers[j].a, self.manufacturers[mother].retailers[
                        j].a = self.manufacturers[mother].retailers[j].a, self.manufacturers[father].retailers[j].a
                    if (self.get_crossover_mono_demand(father) > config.P or self.get_crossover_mono_demand(mother) > config.P):
                        self.manufacturers[father].retailers[j].a, self.manufacturers[mother].retailers[
                            j].a = self.manufacturers[mother].retailers[j].a, self.manufacturers[father].retailers[j].a
            # crossover n_j
            for j in range(len(config.H_r)):
                if random.randrange(2) == 1:
                    self.manufacturers[father].n[j], self.manufacturers[mother].n[
                        j] = self.manufacturers[mother].n[j], self.manufacturers[father].n[j]
            self.manufacturers[father].caculator_C()
            self.manufacturers[mother].caculator_C()

    def mutation(self):
        for i in range(int(self.n*self.p_mutation)):
            index = random.randrange(self.n)
            # mutation A
            while self.get_crossover_mono_demand(index) > config.P:
                self.manufacturers[index].A = random.randrange(1, self.H)

            # mutation a
            while self.get_crossover_mono_demand(index) > config.P:
                for j in range(len(config.e_a)):
                    if random.randrange(2) == 1:
                        self.manufacturers[index].retailers[j].a = random.randrange(
                            1, self.H)

            # mutation n
            for j in range(len(config.M)):
                if random.randrange(2) == 1:
                    self.manufacturers[index].n[j] = random.randint(2, 20)
            self.manufacturers[index].caculator_C()

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
