import json
import logging
from aiokafka import AIOKafkaProducer
from oar.settings import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_DEDUPE_BASIC_NAME

logger = logging.getLogger(__name__)


async def produce_message_match_process(source_id):
    logger.info('Inside method - produce_message_match_process')
    logger.info('Servers: {}'.format(KAFKA_BOOTSTRAP_SERVERS))
    logger.info('Topic: {}'.format(KAFKA_TOPIC_DEDUPE_BASIC_NAME))
    if KAFKA_BOOTSTRAP_SERVERS == '' or KAFKA_TOPIC_DEDUPE_BASIC_NAME == '':
        return

    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS
    )
    # get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        # produce message
        await producer.send(KAFKA_TOPIC_DEDUPE_BASIC_NAME,
                            json.dumps(source_id).encode())
        logger.info('Produce Message with source_id {}'.format(source_id))
    except Exception as exc:
        logger.info('Produce Message with error {}'.format(exc))
    finally:
        # wait for all pending messages to be delivered or expire.
        await producer.stop()
