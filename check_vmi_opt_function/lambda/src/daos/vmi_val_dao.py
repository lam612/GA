import os
import json
import traceback
import logging
import boto3
from boto3.dynamodb.conditions import Key
from ..constants import JobStatus


logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class VMIValDao:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = boto3.session.Session()
        endpoint_url = None
        # if os.getenv('ENDPOINT_URL', None) is not None and os.getenv('ENDPOINT_URL', None).strip() != 'None':
        #     endpoint_url = os.getenv('ENDPOINT_URL')
        endpoint_url = "http://localhost:4566"
        self.client = self.session.client(
            service_name='dynamodb',
            endpoint_url=endpoint_url
        )
        self.resource = self.session.resource(
            service_name='dynamodb',
            endpoint_url=endpoint_url
        )
        print("[DAO] Table name : {}".format(
            os.getenv('TABLE_NAME', "VMI_VARIABLE")))
        TABLE_NAME = "VMI_VARIABLE"

        # self.table = self.resource.Table(os.environ['TABLE_NAME'])
        self.table = self.resource.Table(TABLE_NAME)

    def query_by_id(self, id: str):
        try:
            response = self.table.get_item(
                Key={
                    "idx": id
                }
            )
            if 'Item' in response:
                return response['Item']
            return None
        except Exception as e:
            self.logger.error("ERROR: Failed to get item from DynamoDB")
            self.logger.error(str(e))
            traceback.print_exc()
            raise e
