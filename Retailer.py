# -*- coding: utf-8 -*-
import numpy as np


class Retailer:

    # init
    # e_a: Độ co giãn quảng cáo của nhà bán lẻ i
    # K: Quy mô thị trường của nhà bán lẻ i
    # phi: Chi phí vận chuyển cho nhà bán lẻ i
    # uc: Nhà sản xuất quản lý hàng tồn kho của nhà bán lẻ i và lấy chi phí uci với mỗi sản phẩm
    # cp: Giá mua 1 sản phẩm từ nhà bán lẻ i
    # H_b: Chi phí giữ hàng phía nhà bán lẻ i
    # L_b: Backorder cost của nhà bán lẻ i
    # S_b: Chi phí cố định bổ sung cho nhà bán lẻ i
    # p: Giá bán sản phẩm của nhà bán lẻ i
    # a: chi phí quảng cáo của nhà bán lẻ i
    # theta: Lợi nhuận mở rộng
    # b: tỉ lệ thời gian tồn đọng hàng trong 1 chu kỳ của nhà bán lẻ i

    def __init__(self, e_a, K, phi, uc, cp, H_b, L_b, S_b, p, e_p, a):
        self.e_a = e_a
        self.K = K
        self.phi = phi
        self.uc = uc
        self.cp = cp
        self.H_b = H_b
        self.L_b = L_b
        self.S_b = S_b
        self.p = p
        self.e_p = e_p
        self.a = a
        self.theta = 0
        self.b = 0

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
