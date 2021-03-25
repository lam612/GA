# -*- coding: utf-8 -*-
import numpy as np
import math
import config


class Manufacturer:
    # init
    # cm: Chi phí sản xuất 1 sản phẩm ($/unit)
    # cr: Chi phí mua 1 đơn vị nguyên liệu thô ($/unit)
    # H_p: Chi phí giữ hàng phía nhà sản xuất ($/unit/time)
    # H_r: Chi phí giữ nguyên liệu thô ($/unit/time) (Mảng gồm l phần tử)
    # M: Số nguyên liệu thô để sản xuất 1 sản phầm (Mảng gồm l phần tử)
    # P: Công suất nhà sản xuất
    # S_p: Chi phí thiết lập sản xuất của nhà sản xuất ($/setup)
    # S_r: Chi phí mua nguyên liệu thô cố định ($/order) (Mảng gồm l phần tử)
    # A: Chi phí quảng cáo của nhà sản xuất
    # e_A: Độ co giãn quảng cáo của nhà sản xuất
    # C: Chu kỳ bổ sung sản phẩm cho nhà bán lẻ
    # n: Chu kỳ mua nguyên liệu thô là C*n (Mảng gồm l phần tử)

    def __init__(self, A, n, x):
        self.cm = config.cm
        self.cr = config.cr
        self.H_p = config.H_p
        self.H_r = config.H_r
        self.M = config.M
        self.P = config.P
        self.S_p = config.S_p
        self.S_r = config.S_r
        self.e_A = config.e_A
        self.retailers = []
        self.A = A
        self.C = 0
        self.n = n
        self.x = x

    # Thêm các nhà bán lẻ vào retailers
    def add_retailer(self, retailer):
        self.retailers.append(retailer)

    # Lợi nhuận NP_M = Tổng thu TR_M - Tổng chi TC_M
    def get_mf_profit(self):
        NP_M = self.get_TR_M() - self.get_TC_M()
        return NP_M

    def get_rt_profit(self, rt_id):
        return self.retailers[rt_id].get_profit(self.A, self.e_A)

    def get_rt_total_profit(self):
        return sum([self.get_rt_profit(id) for id in range(len(self.retailers))])

    def get_model_profit(self):
        return self.get_mf_profit() + self.get_rt_total_profit()

    def get_model_demand(self):
        return sum([rt.get_demand(self.A, self.e_A) for rt in self.retailers])

    # TR_M có 3 thành phần
    # 1: Giá bán buôn sản phẩm
    # 2: Chi phí coi hàng được trả bởi nhà bán lẻ
    # 3: Lợi nhuận mở rộng
    def get_TR_M(self):
        TR_M = 0
        for i in range(len(self.retailers)):
            demand_i = self.retailers[i].get_demand(self.A, self.e_A)

            TR_M += demand_i * self.retailers[i].cp
            TR_M += demand_i * self.retailers[i].uc
            TR_M += demand_i * self.retailers[i].theta
        return TR_M

    # TC_M gồm:
    # Tổng chi phí trực tiếp TDC_M
    # Tổng chi phí gián tiếp TIDC_M

    def get_TC_M(self):
        TC_M = self.get_TDC_M() + self.get_TIDC_M()
        return TC_M

    # TDC_M gồm :
    # Chi phí sản xuất
    # Chi phí vận chuyển
    # Chi phí mua nguyên liệu
    def get_TDC_M(self):
        TDC_M = 0
        for i in range(len(self.retailers)):
            demand_i = self.retailers[i].get_demand(self.A, self.e_A)
            TDC_M += demand_i * self.cm
            TDC_M += demand_i * self.retailers[i].phi
            for j in range(len(self.M)):
                TDC_M += demand_i * self.M[j] * self.cr[j]
        return TDC_M

    # TIDC_M gồm 3 chi phí con CC
    # Tổng chi phí nhà sản xuất bồi thường cho nhà bán lẻ
    # Tổng chi phí tồn kho TIC
    # Tổng chi phí quảng cáo A
    def get_TIDC_M(self):
        TIDC_M = self.get_CC() + self.get_TIC() + self.A
        return TIDC_M

    # CC gồm:
    # Chi phí ordering, holding, backordering

    def get_CC(self):
        CC = 0
        for i in range(len(self.retailers)):
            demand_i = self.retailers[i].get_demand(self.A, self.e_A)
            CC += self.retailers[i].S_b / self.C
            CC += demand_i * \
                (1-self.retailers[i].b)**2 * \
                self.C * self.retailers[i].H_b / 2
            CC += demand_i * \
                self.retailers[i].b**2 * self.C * \
                self.retailers[i].L_b / 2
        return CC

    # TIC gồm
    # TIC_p : Chi phí giữ sản phẩm
    # TIC_r : Chi phí giữ nguyên liệu thô
    def get_TIC(self):
        TIC = self.get_TIC_p() + self.get_TIC_r()
        return TIC

    # TIC_p goomf:
    # Chi phí thiết lập sản xuất
    # Chi phí giữ hàng phía nhà bán lẻ
    def get_TIC_p(self):
        TIC_p = 0
        TIC_p += self.x * self.S_p / self.C
        for i in range(len(self.retailers)):
            demand_i = self.retailers[i].get_demand(self.A, self.e_A)
            TIC_p += self.H_p * self.C / (2*self.P) * demand_i**2
        return TIC_p

    # TIC_r gồm :
    # Chi phí đặt nguyên liệu thô cố định
    # Chi phí giữ nguyên liệu thô
    def get_TIC_r(self):
        TIC_r = 0
        for j in range(len(self.M)):
            TIC_r += (self.S_r[j] + self.get_HIC(j)) / (self.n[j] * self.C)
        return TIC_r

    # get_HIC gồm :
    # Chi phí giữ nguyên liệu trong quá trình sản xuất HIC_d
    # Chi phí giữ nguyên liệu trong kho HIC_r
    def get_HIC(self, j):
        HIC = self.get_HIC_d(j) + self.get_HIC_r(j)
        return HIC

    def get_HIC_d(self, j):
        X = 0
        for i in range(len(self.retailers)):
            demand_i = self.retailers[i].get_demand(self.A, self.e_A)
            X += demand_i * self.C
        HIC_d = self.n[j] * self.M[j] * self.H_r[j] * X**2 / (2*self.P)
        return HIC_d

    def get_HIC_r(self, j):
        X = 0
        for i in range(len(self.retailers)):
            demand_i = self.retailers[i].get_demand(self.A, self.e_A)
            X += demand_i
        HIC_r = self.n[j] * (self.n[j] - 1) * self.M[j] * \
            self.H_r[j] * X * self.C**2 / 2
        return HIC_r

    def calc_C(self):
        # X là tổng của Sb_i
        # Y là tổng của các nhu cầu
        X = 0
        Y = 0
        H1 = 0
        H2 = 0
        for i in range(len(self.retailers)):
            demand_i = self.retailers[i].get_demand(self.A, self.e_A)
            L_b = self.retailers[i].L_b
            H_b = self.retailers[i].H_b
            X += self.retailers[i].S_b
            Y += demand_i
            H1 += self.H_p * demand_i**2 / self.P
            H1 += demand_i * L_b * H_b / (L_b + H_b)
        H2 = H1 / self.P
        H1 /= Y
        for j in range(len(self.M)):
            H1 += self.M[j] * self.H_r[j] * (self.n[j] - 1 + Y/self.P)
            H2 += self.M[j] * self.H_r[j] * self.n[j]
        # Z là tổng của Srj/nj
        Z = 0
        for j in range(len(self.M)):
            Z += self.S_r[j] / self.n[j]

        if self.x == 1:
            C_1 = 2 * (X + self.S_p + Z) / (H1*Y)
            self.C = math.sqrt(C_1)
        elif x == 0:
            C_2 = 2*(X + Z) / (H2*P)
            self.C = math.sqrt(C_2)
