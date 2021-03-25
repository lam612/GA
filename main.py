# -*- coding: utf-8 -*-
import numpy as np
import config
import sys

from GA import GA

population = 1000
generation_count = 1000

ga = GA(population)

ga.create()
print("{}".format(204 * "-"))
print("|{:^19s} | {:^54} | {:^123}|".format(
    "OPTIMAL", "MANUFACTURER", "RETAILER"))
print("{}".format(204 * "-"))
print('[{:^3s}] | {:^12s} | {:^8s} | {:^6s} | {:^8s} | {:^10s}'.format(
    'STT', '#NP', 'A', 'C', 'DEMAND', 'NP_M'), end='')
for i in range(len(config.M)):
    print('| {:^5s}'.format('n' + str(i+1)), end='')
for i in range(len(config.K)):
    idx = str(i+1)
    print('| {:^8s} | {:^12s}'.format('a' + idx, "NP_b" + idx), end='')
print("|\n{}".format(204 * "-"))
for i in range(generation_count):
    ga.evaluation()
    ga.selection()
    ga.crossover()
    ga.mutation()
    if i % (generation_count / 50) == 0:
        print('[{:>3d}] | '.format(i), end='')
        ga.show_optimal()


manufacture = ga.get_best_mf()
e_A = manufacture.e_A
A = manufacture.A
sum_e_bi = 0
for i in range(len(config.e_a)):
    sum_e_bi += manufacture.retailers[i].e_a
sys.exit()

for i in range(len(config.e_a)):
    pi = manufacture.retailers[i].p
    cpi = manufacture.retailers[i].cp
    uci = manufacture.retailers[i].uc
    e_bi = manufacture.retailers[i].e_a
    bi = manufacture.retailers[i].b
    delta_NP_bi = (e_bi/(e_A + sum_e_bi))*ga.manufacture.get_rt_total_profit()
    NP_bi = manufacture.retailers[i].get_profit(A, e_A)
    a_i = manufacture.retailers[i].a
    deman_i = manufacture.retailers[i].get_demand(A, e_A)
    manufacture.retailers[i].PP = pi - cpi - \
        uci - 1.0 * (delta_NP_bi + NP_bi + a_i)/deman_i
a = int(ga.profit_list[ga.best_id]/3) + int(manufacture.get_mf_profit())
print("\n")
print("   Nhà sản xuất: ")
print("   x: ", manufacture.x)
print("   nj: ", manufacture.n)
print("   C: ", manufacture.C)
text = "   ------------------------------------------------------------------------------" + "\n"
text += "   |              Chi phí quảng cáo                |         Lợi nhuận          |" + "\n"
text += "   ------------------------------------------------------------------------------" + "\n"
text += "   |              " + \
    str(manufacture.A) + "                            |          " + \
    str(a) + "             |" + "\n"
text += "   ------------------------------------------------------------------------------"
print(text)

print("")
print("   Nhà bán lẻ:")
text = "   -------------------------------------------------------------------------------------------------" + "\n"
text += "   |    STT    |      bi      |     Chi phí quảng cáo     |      theta      |       Lợi nhuận       |" + "\n"
text += "   -------------------------------------------------------------------------------------------------" + "\n"
for i in range(len(config.e_a)):
    text += "   |     " + str(i) + "     |    " + str(round(manufacture.retailers[i].b, 4)) + "    |         " + str(round(manufacture.retailers[i].a, 4)) + "             |    " + str(
        round(manufacture.retailers[i].theta, 4)) + "    |       " + str(int(manufacture.retailers[i].get_profit(A, e_M))) + "       |" + "\n"
    text += "   -------------------------------------------------------------------------------------------------" + "\n"
print(text)
