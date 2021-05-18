import traceback
import logging
import hashlib
import json
from ..daos import VMIValDao
from botocore.exceptions import ClientError
from ..constants import JobStatus

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


class VMIValService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = VMIValDao()

    def process(self, vmi_id):
        data = self.db.query_by_id(vmi_id)
        if data is None:
            return None
        response = {
            'status': data['status'],
            'vmi_val': json.loads(data['vmi_val'])
        }
        if data['status'] != JobStatus.CREATED:
            nash_strategy = data.get('nash_strategy', None)
            nash_ga_log = data.get('nash_ga_log', None)
            if nash_strategy != '' and nash_strategy != None:
                response['nash_strategy'] = json.loads(nash_strategy)
                response['nash_ga_log'] = json.loads(nash_ga_log)
        return response
