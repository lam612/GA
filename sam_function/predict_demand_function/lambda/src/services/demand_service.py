import os
from io import BytesIO
import boto3
import json
import traceback
import logging
import joblib

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class DemandService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = boto3.session.Session()
        endpoint_url = None
        if os.getenv('ENDPOINT_URL', None) is not None and os.getenv('ENDPOINT_URL', None).strip() != 'None':
            endpoint_url = os.getenv('ENDPOINT_URL')
        self.client = self.session.client(
            service_name='s3',
            endpoint_url=endpoint_url
        )
        self.resource = self.session.resource(
            service_name='s3',
            endpoint_url=endpoint_url
        )
        self.s3_bucket = os.environ['S3_Name']
        self.model_bucket = self.resource.Bucket(self.s3_bucket)
        self.model_file_name = os.environ['MODEL_S3_NAME']
        self.df = None
        self.model = None
        self.read_joblib()

    def read_joblib(self):
        with BytesIO() as f:
            self.client.download_fileobj(
                Bucket=self.model_bucket, Key=self.model_file_name, Fileobj=f)
            f.seek(0)
            self.model = joblib.load(f)

    def process(self, manu_discount, retailer_discount, sell_price):
        prediction_result = self.model.predict(
            [[manu_discount, retailer_discount, sell_price]])
        return prediction_result
