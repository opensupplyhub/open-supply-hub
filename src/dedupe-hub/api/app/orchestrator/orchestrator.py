import logging
import json

from app.utils.helpers import transform_to_dict
from app.database.sqlalchemy import get_session
from app.database.models.facility import Facility

log = logging.getLogger(__name__)

class Orchestrator():
    '''
    The singleton class that handles POST requests to v1 endpoints and DedupeHub:
    1. Get data from Kafka producer
    2. Search related data in the PostgreSQL
    3. Transform data received from the PostgreSQL
    4. Pass it to specific Kafka topic
    '''

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Orchestrator, cls) \
                .__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self):
        pass

    @staticmethod
    async def produce_data(producer, kafka_topic, os_id):
        try:
            # You need to convert to JSON object that you will receive from DB
            result = Orchestrator.__sync_data(os_id)
            await producer.send(kafka_topic, json.dumps(result).encode())
            log.info(f'[Kafka] Sent message to moderation-events topic: {result}')
        except Exception as error:
            log.error(f'[Orchestrator] Error: {error}')
            return
        finally:
            await producer.stop()

    @staticmethod
    def __sync_data(os_id):
        with get_session() as session:
            # Use query to the Facility
            # TODO: Pass specific schema to this method, it should conform schema that ingested to the OpenSearch

            production_location = session.query(
                Facility.id,
                Facility.country_code,
                Facility.name,
                Facility.address
            ).filter(Facility.id == os_id).all()

            return transform_to_dict(production_location)

