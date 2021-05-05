import os
import boto3
import json
import traceback
import logging
from time import time
from dotenv import load_dotenv
import pandas as pd
import pickle
from sklearn import linear_model
from boto3.dynamodb.conditions import Key, Attr

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)

load_dotenv()


class PredictDemandModel:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = boto3.session.Session(
            aws_access_key_id=os.environ["ACCESS_KEY"],
            aws_secret_access_key=os.environ["SECRET_KEY"],
            profile_name='Law')
        self.client = self.session.client(
            service_name='s3'
        )
        self.resource = self.session.resource(
            service_name='s3'
        )
        self.data_path = os.environ["DATA_PATH"]
        self.model_path = os.environ["MODEL_PATH"]
        self.model_val = None

    def build_model(self):
        df = pd.read_csv(self.data_path)
        X = df[['manu_discount', 'retailer_discount',
                'selling_price']].astype(float)
        Y = df['demand'].astype(float)
        model = linear_model.LinearRegression()
        model.fit(X, Y)
        self.model_val = {
            "coef": model.coef_.tolist(),
            "intercept": model.intercept_
        }
        with open(self.model_path, 'w+') as fp:
            json.dump(self.model_val, fp)
        return self.model_val

    def get_model_val(self, rebuild_model: int):
        if(rebuild_model == 0):
            with open(self.model_path, 'r') as fp:
                self.model_val = json.load(fp)
        else:
            self.model_val = self.build_model()
        return self.model_val
