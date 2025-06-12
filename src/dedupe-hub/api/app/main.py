import asyncio
import json
import logging

from random import randint
from typing import Set, Any
from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from kafka import TopicPartition

from app.utils.rollbar import init_rollbar
from app.matching.matcher.gazeteer.gazetteer_cache import GazetteerCache

from app.config import settings

from app.matching.facilities_matcher import matcher

import app.database.signals.origin_source

# Fast API instance
app = FastAPI()

# global variables
consumer_task = None
consumer = None

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    log.info('Initializing API ...')
    init_rollbar()
    await build_gazetteer()
    res = await initialize()
    if res:
        await consume()


@app.on_event("shutdown")
async def shutdown_event():
    log.info('Shutting down API')
    consumer_task.cancel()
    await consumer.stop()


@app.get("/")
async def root():
    return {"message": "Hello from Kafka & Fast API app."}

@app.get("/trigger/{source_id}")
async def trigger(source_id):
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.bootstrap_servers
    )
    # get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        # produce message
        await producer.send(settings.topic_dedupe_basic_name, json.dumps(source_id).encode())
    finally:
         # wait for all pending messages to be delivered or expire.
        await producer.stop()

    message = "Kafka Producer try to send message '{0}' to topic '{1}'".format(source_id, settings.topic_dedupe_basic_name)

    return {
        "message": message
    }

async def initialize():
    loop = asyncio.get_event_loop()
    global consumer
    group_id = f'{settings.consumer_group_id}-{randint(0, 10000)}'
    log.debug(f'Initializing KafkaConsumer for topic {settings.topic_dedupe_basic_name}, group_id {group_id}'
              f' and using bootstrap servers {settings.bootstrap_servers}')
    consumer = AIOKafkaConsumer(settings.topic_dedupe_basic_name, loop=loop,
                                         bootstrap_servers=settings.bootstrap_servers,
                                         group_id=group_id)
    # get cluster layout and join group
    await consumer.start()

    partitions: Set[TopicPartition] = consumer.assignment()
    nr_partitions = len(partitions)
    if nr_partitions != 1:
        log.warning(f'Found {nr_partitions} partitions for topic {settings.topic_dedupe_basic_name}. Expecting '
                    f'only one, remaining partitions will be ignored!')
    for tp in partitions:

        # get the log_end_offset
        end_offset_dict = await consumer.end_offsets([tp])
        end_offset = end_offset_dict[tp]

        if end_offset == 0:
            log.warning(f'Topic ({settings.topic_dedupe_basic_name}) has no messages (log_end_offset: '
                        f'{end_offset}), skipping initialization ...')
            return True

        log.debug(f'Found log_end_offset: {end_offset} seeking to {end_offset-1}')
        consumer.seek(tp, end_offset-1)
        msg = await consumer.getone()
        log.info(f'Initializing API with data from msg: {msg}')

        # handle matching
        await handle(msg.value)

        return True

async def consume():
    global consumer_task
    consumer_task = asyncio.create_task(send_consumer_message(consumer))

async def send_consumer_message(consumer):
    try:
        # consume messages
        async for msg in consumer:
            # x = json.loads(msg.value)
            log.info(f"Consumed msg: {msg}")

            # handle matching
            await handle(msg.value)
    finally:
        # will leave consumer group; perform autocommit if enabled
        log.warning('Stopping consumer')
        await consumer.stop()

async def handle(value):
    value = json.loads(value.decode("utf-8"))
    log.info(f'[Matching] Source Id: {value}')
    try:
        log.info(f'[Matching] Start processing!')
        result = matcher(value)
        log.info(f'[Matching] Result: {result}')
    except Exception as error:
        log.error(f'[Matching] Error: {error}')
    return

async def build_gazetteer():
    try:
        GazetteerCache.get_latest()
    except Exception as e:
        log.error(f'[Matching] Initial Gazetteer Build Error: {e}')