from .services import NashService
import traceback
import logging
import json

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


def lambda_handler(event, context):
    logger = logging.getLogger(__name__)

    service = NashService()

    try:
        vmi_id = event['vmi_id']
    except KeyError as e:
        logger.error('VMI ID doesn\'t exist')
        logger.error(str(e))
        traceback.print_exc()
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid VMI ID"
            })
        }

    try:
        response = service.process(vmi_id, context)
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
    else:
        return {
            "statusCode": 200,
            "body": json.dumps(response)
        }
