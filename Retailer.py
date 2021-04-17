# -*- coding: utf-8 -*-
import numpy as np
import config
import random


class Retailer:

    # init
    # e_a: Độ co giãn quảng cáo của nhà bán lẻ i
    # K: Quy mô thị trường của nhà bán lẻ i
    # phi: Chi phí vận chuyển cho nhà bán lẻ i
    # uc: Nhà sản xuất quản lý hàng tồn kho của nhà bán lẻ i và lấy chi phí uci với mỗi sản phẩm
    # cp: Giá bán 1 sản phẩm cho nhà bán lẻ thứ i
    # H_b: Chi phí giữ hàng phía nhà bán lẻ i
    # L_b: Backorder cost của nhà bán lẻ i
    # S_b: Chi phí cố định bổ sung cho nhà bán lẻ i
    # p: Giá bán sản phẩm của nhà bán lẻ i
    # a: chi phí quảng cáo của nhà bán lẻ i
    # theta: Lợi nhuận mở rộng
    # b: tỉ lệ thời gian tồn đọng hàng trong 1 chu kỳ của nhà bán lẻ i

    def __init__(self, id=int, a=int, max_AS=0.5):
        self.e_a = config.e_a[id]
        self.K = config.K[id]
        self.phi = config.phi[id]
        self.uc = config.uc[id]
        self.cp = config.cp[id]
        self.H_b = config.H_b[id]
        self.L_b = config.L_b[id]
        self.S_b = config.S_b[id]
        self.p = config.p[id]
        self.e_p = config.e_p[id]
        self.theta = 0
        self.b = 0
        self.max_revenue = self.K * self.p
        self.max_a = self.max_revenue * max_AS
        self.set_a(a)
        self.calculator_b()

    # get_demand: Tính nhu cầu sản phẩm trên mỗi đơn vị thời gian của nhà bán lẻ
    def get_demand(self, A, e_A):
        D = self.K * pow(self.a, self.e_a) * \
            pow(A, e_A) / pow(self.p / self.cp, self.e_p)
        return D

    # get_profit: Tính lợi nhuận của nhà bán lẻ
    # Tổng thu - Tổng chi
    # Nhu cầu * giá bán p - nhu cầu * (giá mua cp + giá trả uc + chi phí mở rộng theta) - chi phí quảng cáo a

    def get_profit(self, A, e_A):
        NP_bi = self.get_demand(
            A, e_A) * (self.p - self.cp - self.uc - self.theta) - self.a
        return NP_bi

    def calculator_b(self):
        self.b = self.H_b / (self.H_b + self.L_b)

    def set_a(self, a):
        self.a = min(self.max_a, a)
        # self.a = a
