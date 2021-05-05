import os
import json
from dotenv import load_dotenv

load_dotenv()


class LRModel:
    def __init__(self):
        self.model = None
        self.get_model_variables()
        self.coef = self.model['coef']
        self.intercept = self.model['intercept']

    def get_model_variables(self):
        with open(os.environ["MODEL_PATH_2"], 'r') as fp:
            # print(json.load(fp))
            self.model = json.load(fp)

    def get_predict_demand(self, A, a, p):
        return A * self.coef[0] + a * self.coef[1] + p * self.coef[2] + self.intercept

    def get_total_predict_value(self, A, list_a, p):
        return sum([self.get_predict_demand(A, list_a[i], p) for i in range(len(list_a))])
