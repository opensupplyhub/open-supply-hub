import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    host = event['host']
    tg_arn = event['tg_arn']

    # return the calculated area as a JSON string
    data = {
        "host": host,
        "tg_arn": tg_arn
    }

    logger.info(f"CLoudWatch logs group: {context.log_group_name}")
    logger.info(f"Registrating targets for {host} and {tg_arn}")
    return json.dumps(data)
