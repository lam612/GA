from .services import VMIValService
import traceback
import logging
import json

logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


def lambda_handler(event, context):
    logger = logging.getLogger(__name__)

    service = VMIValService()

    if event.get("body", None) is None:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid input Error"
            })
        }
    print(type(event["body"]))
    vmi_val = json.loads(event["body"])["vmi_val"]

    try:
        response = service.process(vmi_val)
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
