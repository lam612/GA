
import json
import os


class LinearRegressionModelService():
    def __init__(self):
        self.linear_model_dao = LinearRegressionModelService()

    def get_predict_demand(self, A, a, p):
        print(list_a)
        return A * self.linear_model_dao.coef[0] + a * self.linear_model_dao.coef[1] + p * self.linear_model_dao.coef[2] + self.linear_model_dao.intercept

    def get_total_predict_value(self, A, list_a, list_p):
        print(list_a)
        return sum([self.get_predict_demand(A, list_a[i], list_p[i]) for i in range(len(list_a))])
