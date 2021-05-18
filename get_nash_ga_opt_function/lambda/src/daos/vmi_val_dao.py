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
        self.table = self.resource.Table(
            os.getenv('TABLE_NAME', "VMI_VARIABLE"))

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

    def update_item_status(self, idx: str, status: str):
        try:
            response = self.table.update_item(
                Key={
                    "idx": idx
                },
                UpdateExpression="set #s=:status",
                ExpressionAttributeNames={
                    "#s": "status"
                },
                ExpressionAttributeValues={
                    ":status": status
                },
                ReturnValues='UPDATED_NEW'
            )
            return response['Attributes']
        except Exception as e:
            self.logger.error("ERROR: Failed to update item status DynamoDB")
            self.logger.error(str(e))
            traceback.print_exc()
            raise e

    def update_item(self, idx: str, status: str, nash_strategy, nash_ga_log):
        try:
            response = self.table.update_item(
                Key={
                    "idx": idx
                },
                UpdateExpression="set #s=:status, nash_strategy=:nash_strategy, nash_ga_log=:nash_ga_log",
                ExpressionAttributeNames={
                    "#s": "status"
                },
                ExpressionAttributeValues={
                    ":status": status,
                    ":nash_strategy": nash_strategy,
                    ":nash_ga_log": nash_ga_log
                },
                ReturnValues='UPDATED_NEW'
            )
            return response['Attributes']
        except Exception as e:
            self.logger.error("ERROR: Failed to cancel item DynamoDB")
            self.logger.error(str(e))
            traceback.print_exc()
            raise e
