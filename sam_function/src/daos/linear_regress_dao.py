import os
import json
from dotenv import load_dotenv

load_dotenv()


class LinearRegressionModelDao:
    def __init__(self):
        self.model = self.get_model_variables()
        self.coef = self.model['coef']
        self.intercept = self.model['intercept']

    def get_model_variables(self):
        with open(os.environ["MODEL_PATH_2"], 'r') as fp:
            self.model = json.load(fp)
