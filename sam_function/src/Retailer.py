# -*- coding: utf-8 -*-
import os
import config
import random
import json
from dotenv import load_dotenv
from utils.common import LRModel

load_dotenv()


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

    def __init__(self, id=int, a=int, cp=int):
        self.K = config.K[id]
        self.phi = config.phi[id]
        self.uc = config.uc[id]
        self.cp = config.cp[id]
        self.H_b = config.H_b[id]
        self.L_b = config.L_b[id]
        self.S_b = config.S_b[id]
        self.theta = 0
        self.b = 0
        self.a = a
        self.p = config.p
        self.max_a = config.MAX_a[id]
        self.calculator_b()
        self.model_val = LRModel()

    # get_demand: Tính nhu cầu sản phẩm trên mỗi đơn vị thời gian của nhà bán lẻ
    def get_predict_demand(self, A):
        return self.model_val.get_predict_demand(A, self.a, self.p)

    def get_model_val(self):
        with open(os.environ["MODEL_PATH_2"], 'r') as fp:
            self.model_val = json.load(fp)
        return self.model_val

    def set_ads(self, a):
        self.a = min(self.max_a, a)

    # get_profit: Tính lợi nhuận của nhà bán lẻ
    # Tổng thu - Tổng chi
    # Nhu cầu * giá bán p - nhu cầu * (giá mua cp + giá trả uc + chi phí mở rộng theta) - chi phí quảng cáo a

    def get_profit(self, A):
        NP_bi = self.get_predict_demand(A) * (self.p - self.cp -
                                              self.uc - self.theta) - self.a
        return NP_bi

    def calculator_b(self):
        self.b = self.H_b / (self.H_b + self.L_b)
