import traceback
import logging
import json
import os
from ..daos import VMIValDao
from botocore.exceptions import ClientError

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class VMIValService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_path = os.getenv(
            'DATA_PATH', '/tmp/data.json')
        self.db = VMIValDao()
        self.vmi_val = {}

    def get_vmi_val_by_id(self, vmi_id: str):
        if self.data_path == '/tmp/data.json':
            self.vmi_val = json.loads(self.db.query_by_id(vmi_id)["vmi_val"])
            with open(self.data_path, 'w') as fp:
                json.dump(self.vmi_val, fp)

    def update_item_status(self, vmi_id, status):
        try:
            response = self.db.update_item_status(vmi_id, status)
            return response
        except Exception as e:
            self.logger.error("ERROR: Failed to update item stauts DynamoDB")
            self.logger.error(str(e))
            traceback.print_exc()
            raise e

    def update_item(self, vmi_id: str, status: str, nash_strategy, nash_ga_log):
        try:
            response = self.db.update_item(
                vmi_id, status, nash_strategy, nash_ga_log)
            return response
        except Exception as e:
            self.logger.error("ERROR: Failed to update item strategy DynamoDB")
            self.logger.error(str(e))
            traceback.print_exc()
            raise e
