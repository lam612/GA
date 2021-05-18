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

    def query_item(self, id: str):
        try:
            response = self.table.query(
                IndexName="idx_gsi",
                KeyConditionExpression=Key(
                    'idx').eq(id),
                Select="ALL_PROJECTED_ATTRIBUTES"
            )
            if 'Items' in response:
                if response['Items'][0]:
                    return response['Items'][0]
                return None
            else:
                return None
        except Exception as e:
            self.logger.error('Query DynamoDB failed')
            self.logger.error(str(e))
            traceback.print_exc()
            return None

    def put_item(self, id, vmi_val):
        try:
            response = self.table.put_item(
                Item={
                    'idx': id,
                    'status': JobStatus.CREATED,
                    'vmi_val': vmi_val
                }
            )
            return response
        except Exception as e:
            self.logger.error('Failed to create new vmi model')
            self.logger.error(str(e))
            traceback.print_exc()
            raise e
