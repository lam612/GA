import traceback
import logging
import hashlib
import json
import os
import boto3
from ..daos import VMIValDao
from botocore.exceptions import ClientError
from ..constants import JobStatus
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class VMIValService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = boto3.session.Session()
        self.db = VMIValDao()
        endpoint_url = None
        if os.getenv('ENDPOINT_URL', None) is not None and os.getenv('ENDPOINT_URL', None).strip() != 'None':
            endpoint_url = os.getenv('ENDPOINT_URL')
        self.client = self.session.client(
            service_name='lambda',
            endpoint_url=endpoint_url,
            region_name=os.environ['REGION']
        )
        self.dl_function_name = os.environ['FUNCTION_NAME']

    def process(self, vmi_val):
        id_json = json.dumps(vmi_val)
        id = hashlib.md5(id_json.encode("utf-8")).hexdigest()
        response = self.db.query_item(id)
        print("[+] Response : {}".format(response))
        if response:
            return {
                "id": id,
                "status": response["status"]
            }
        else:
            try:
                response = self.db.put_item(id, vmi_val)
                if os.getenv('LAMBDA_ENDPOINT_URL', None) is not None and os.getenv('LAMBDA_ENDPOINT_URL', None).strip() != 'None':
                    log_type = 'Tail'
                else:
                    log_type = 'None'
                with ThreadPoolExecutor(1) as e:
                    future = e.submit(
                        self.client.invoke,
                        FunctionName=self.dl_function_name,
                        InvocationType='Event',
                        LogType=log_type,
                        Payload=json.dumps({
                            'vmi_id': id
                        }))
                future.result()
                return {
                    "id": id,
                    "status": JobStatus.CREATED
                }
            except ClientError as e:
                if e.response['Error']['Code'] == 'LimitExceededException':
                    self.logger.warn(
                        'API call limit exceeded; backing off and retrying...')
                self.logger.warn(str(e))
                traceback.print_exc()
                raise e
