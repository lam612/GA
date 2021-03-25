from .services import JobService
from .config import AwsConfig
import traceback
import logging
import json

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


def lambda_handler(event, context):
    logger = logging.getLogger(__name__)

    AwsConfig().config()
    service = JobService()

    try:
        job_id = json.loads(event['body'])['job_id']
    except KeyError as e:
        logger.error('Key doesn\'t exist')
        logger.error(str(e))
        traceback.print_exc()
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid input Error"
            })
        }
    if job_id == '':
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "job_id Validation Error"
            })
        }
    else:
        try:
            response = service.process(job_id)
        except Exception as e:
            logger.error('Server Internal Error')
            logger.error(str(e))
            traceback.print_exc()
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": "Server Internal Error"
                })
            }

        if response is None:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "job_id Validation Error"
                })
            }
        else:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": response['status'],
                    "info": response.get('info', None)
                }),
            }
