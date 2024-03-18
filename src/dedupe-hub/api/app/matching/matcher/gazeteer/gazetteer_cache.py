import logging
from typing import Dict, List, Tuple, Union
from dedupe import Gazetteer, StaticGazetteer
from sqlalchemy.sql import func

from app.utils.rollbar import try_reporting_error_to_rollbar
from app.database.sqlalchemy import get_session
from app.exceptions import NoCanonicalRecordsError
from app.database.models.facility import Facility
from app.database.models.facility_match import FacilityMatch
from app.database.models.historical_facility import HistoricalFacility
from app.database.models.historical_facility_match import HistoricalFacilityMatch
from app.utils.helpers import transform_to_dict
from app.matching.matcher.gazeteer.gazetteer_helper import (
    facility_values_to_dedupe_record,
    match_detail_to_extended_facility_id,
)
from app.matching.matcher.gazeteer.gazetteer_data_fetcher import (
    get_canonical_items,
    get_messy_items_for_training,
)
from app.matching.matcher.gazeteer.gazetteer_train import gazetteer_train

logger = logging.getLogger(__name__)

FacilityValues = Dict[int, Dict[str, Dict[str, str]]]
FacilityHistory = Tuple[List[HistoricalFacility], FacilityValues]
LatestMatchRecords = Dict[int, Dict[str, bool or str or int]]
MatchHistory = Tuple[
    List[HistoricalFacilityMatch], LatestMatchRecords, FacilityValues
]


class GazetteerCache:
    """
    A container for holding a single, trained and indexed Gazetteer in memory,
    which is updated with any `Facility` rows that have been added, updated, or
    removed since the previous call to the `get_latest` class method.

    Note that the first time `get_latest` is called it will be slow, as it
    needs to train a model and index it with all the `Facility` items.
    """
    _gazetter: Union[Gazetteer, StaticGazetteer, None] = None
    _facility_version: Union[int, None] = None
    _match_version: Union[int, None] = None

    @classmethod
    def _rebuild_gazetteer(cls) -> Union[Gazetteer, StaticGazetteer, None]:
        logger.info('Rebuilding gazetteer')
        with get_session() as session:
            db_facility_version = (
                session.query(func.max(HistoricalFacility.history_id).label("max_id")).limit(1)
            )
            db_match_version = (
                session.query(func.max(HistoricalFacilityMatch.history_id).label("max_id")).limit(1)
            )

            # We expect `get_canonical_items` to return a list rather than a
            # QuerySet so that we can close the transaction as quickly as
            # possible
            canonical = get_canonical_items()
            if len(canonical.keys()) == 0:
                raise NoCanonicalRecordsError()
            # We expect `get_messy_items_for_training` to return a list rather
            # than a QuerySet so that we can close the transaction as quickly
            # as possible
            messy = get_messy_items_for_training()
            cls._gazetter = gazetteer_train(messy, canonical, should_index=True)
            cls._facility_version = db_facility_version
            cls._match_version = db_match_version
            return cls._gazetter

    @classmethod
    def _get_new_facility_history(cls) -> FacilityHistory:
        facility_changes = []
        latest_facility_dedupe_records = {}
        with get_session() as session:
            db_facility_version = (
                session.query(func.max(HistoricalFacility.history_id).label("max_id")).limit(1)
            )

            if db_facility_version != cls._facility_version:
                if cls._facility_version is None:
                    last_facility_version_id = 0
                else:
                    last_facility_version_id = cls._facility_version
                # We call `list` so that we can get all the data and exit
                # the transaction as soon as possible
                historical_facility_q = session.query(
                    HistoricalFacility.id, 
                    HistoricalFacility.country_code, 
                    HistoricalFacility.name, 
                    HistoricalFacility.address, 
                    HistoricalFacility.history_type, 
                    HistoricalFacility.history_id
                ). \
                filter(
                    HistoricalFacility.history_id == last_facility_version_id
                ). \
                order_by(
                    HistoricalFacility.history_id.desc()
                )
                facility_changes: List[Dict[str, str or int]] = []
                for item in historical_facility_q:
                    dict_item = {
                        'id': item.id,
                        'country': item.country_code,
                        'name': item.name,
                        'address': item.address,
                        'history_type': item.history_type,
                        'history_id': item.history_id
                    }
                    facility_changes.append(dict_item)

                changed_facility_ids_qs = [item.id for item in historical_facility_q]
                # We use an dictionary comprehension so that we can load
                # all the data and exit the transaction as soon as possible
                latest_facility_dedupe_records = {
                    f['id']: facility_values_to_dedupe_record(f)
                    for f in
                    transform_to_dict(session.query(Facility.id, Facility.country_code, Facility.name, Facility.address). \
                        filter(Facility.id.in_(changed_facility_ids_qs)))
                }

            return facility_changes, latest_facility_dedupe_records

    @classmethod
    def _get_new_match_history(cls) -> MatchHistory:
        match_changes = []
        latest_match_records = {}
        latest_matched_facility_dedupe_records = {}
        with get_session() as session:
            db_match_version = session.query(func.max(HistoricalFacility.history_id).label("max_id")).limit(1)

            if db_match_version != cls._match_version:
                if cls._match_version is None:
                    last_match_version_id = 0
                else:
                    last_match_version_id = cls._match_version

                # We call `list` so that we can get all the data and exit
                # the transaction as soon as possible
                match_changes = list(
                    session.query(
                    HistoricalFacilityMatch.id, 
                    HistoricalFacilityMatch.facility_id, 
                    HistoricalFacilityMatch.history_type, 
                    HistoricalFacilityMatch.history_id
                    ). \
                    filter(
                        HistoricalFacilityMatch.history_id==last_match_version_id
                    ). \
                    order_by(HistoricalFacilityMatch.history_id.desc())
                )

                # We use an dictionary comprehension so that we can load
                # all the data and exit the transaction as soon as possible
                history_id_list = [item.history_id for item in match_changes]
                latest_match_records = {
                    m['id']: {
                        'facility': m['facility_id'],
                        'status': m['status'],
                        'is_active': m['is_active'],
                    } for m in session.query(FacilityMatch.id, 
                                             FacilityMatch.facility_id, 
                                             FacilityMatch.status, 
                                             FacilityMatch.is_active). \
                        filter(
                            FacilityMatch.id.in_(history_id_list)
                        )
                }

                # We use an dictionary comprehension so that we can load
                # all the data and exit the transaction as soon as possible
                facility_id_list = [item.facility_id for item in match_changes]
                latest_matched_facility_dedupe_records = {
                    f['id']: facility_values_to_dedupe_record(f) for f in
                    transform_to_dict(session.query(Facility).filter(Facility.id.in_(facility_id_list)))
                }

            return (match_changes, latest_match_records,
                    latest_matched_facility_dedupe_records)

    @classmethod
    def get_latest(cls) -> Gazetteer or StaticGazetteer or None:
        try:
            if cls._gazetter is None:
                return cls._rebuild_gazetteer()

            facility_changes, latest_facility_dedupe_records = \
                cls._get_new_facility_history()

            for item in facility_changes:
                # We were previously calling `cls._gazetter.unindex` to
                # remove records with a `history_type` of `-` but it was
                # raising exceptions for which we could not determine the
                # root cause. We have opted to ignore them and filter out
                # no longer existing records from the match results.
                if item['history_type'] != '-':
                    # The history record has old field values, so we use the
                    # updated version that we fetched. If we don't have a
                    # record for the ID, it means that the facility has been
                    # deleted. We don't need to index a deleted facility.
                    if item['id'] in latest_facility_dedupe_records:
                        record = latest_facility_dedupe_records[item['id']]
                        logger.debug(
                            'Indexing facility {}'.format(str(record)))
                        cls._gazetter.index(record)
                cls._facility_version = item['history_id']

            (match_changes, latest_match_records,
             latest_matched_facility_dedupe_records) = \
                cls._get_new_match_history()

            def dedupe_record_for_match_item(
                item: FacilityMatch
            ) -> Dict[str, Dict[str, str]]:
                facility_id = item.facility_id
                key = match_detail_to_extended_facility_id(
                    facility_id, item.id)
                """
                The latest_matched_facility_dedupe_records dictionary looks
                like this:

                {
                    facility_id: {
                        facility_id: {
                            field1: value1,
                            field2, value2
                        }
                    }
                }

                We want to get the inner object and change the key from a real
                facility ID to a "synthetic" facility ID which we use to index
                confirmed matches.
                """
                value = (
                    latest_matched_facility_dedupe_records
                    [facility_id][facility_id]
                )
                return {key: value}

            for item in match_changes:
                match = (latest_match_records[item['id']]
                         if item['id'] in latest_match_records
                         else None)
                has_facility = (
                    item['facility_id'] in latest_matched_facility_dedupe_records)
                is_confirmed_match_with_facility = (
                    match
                    and match['status'] == FacilityMatch.CONFIRMED
                    and has_facility)
                if is_confirmed_match_with_facility:
                    # We were previously calling `cls._gazetter.unindex` to
                    # remove records with a `history_type` of `-` but it was
                    # raising exceptions for which we could not determine the
                    # root cause. We have opted to ignore them and filter out
                    # no longer existing records from the match results.
                    if item['history_type'] != '-':
                        # The history record has old field values, so we us the
                        # updated version that we fetched. If we don't have a
                        # record for the ID, it means that the facility has
                        # been deleted. We don't need to index a deleted
                        # facility.
                        if match and match['is_active']:
                            record = dedupe_record_for_match_item(item)
                            logger.debug(f'Indexing match {record}')
                            cls._gazetter.index(record)
                    cls._match_version = item['history_id']

        except Exception as e:
            try_reporting_error_to_rollbar(extra_data={
                'last_successful_facility_version': cls._facility_version,
                'last_successful_match_version': cls._match_version
            }, exception=e)
            raise

        return cls._gazetter
