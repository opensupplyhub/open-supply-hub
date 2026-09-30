import logging
from typing import Dict, List, Tuple, Union
from dedupe import Gazetteer, StaticGazetteer
from sqlalchemy import select
from sqlalchemy.sql import func

from app.utils.rollbar import try_reporting_error_to_rollbar
from app.database.sqlalchemy import get_session
from app.exceptions import NoCanonicalRecordsError
from app.database.models.facility import Facility
from app.database.models.facility_list_item import FacilityListItem
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
        # The version markers are read in their own short-lived session. They
        # have to be read *before* training so that anything written while the
        # model trains is picked up by the next incremental refresh rather than
        # skipped, but training and indexing take minutes, and leaving this
        # session open around them would hold a connection `idle in
        # transaction` on the primary for that whole time, pinning a snapshot
        # against VACUUM and exposing the rebuild to
        # `idle_in_transaction_session_timeout`.
        with get_session() as session:
            db_facility_version = session.query(
                func.max(HistoricalFacility.history_id)
            ).scalar()
            db_match_version = session.query(
                func.max(HistoricalFacilityMatch.history_id)
            ).scalar()

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
            db_facility_version = session.query(
                func.max(HistoricalFacility.history_id)
            ).scalar()

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
                    HistoricalFacility.history_id > last_facility_version_id
                ). \
                order_by(
                    HistoricalFacility.history_id.asc()
                )
                # `historical_facility_q` is a Query, so every iteration of
                # it issues the statement again. It is materialized once here
                # and reused: now that the filter is `>` rather than `==` the
                # result set is the whole backlog, not a single row, and the
                # second pass would both double the work and read a different
                # READ COMMITTED snapshot.
                facility_changes: List[Dict[str, str or int]] = [
                    {
                        'id': item.id,
                        'country': item.country_code,
                        'name': item.name,
                        'address': item.address,
                        'history_type': item.history_type,
                        'history_id': item.history_id
                    }
                    for item in historical_facility_q.all()
                ]

                # The changed ids are passed as a subquery rather than as a
                # materialized list of bind parameters. The backlog is
                # unbounded for the same reason as above, and one parameter
                # per row would run into PostgreSQL's 65535 bind-parameter
                # limit, which `get_latest` re-raises rather than degrading.
                changed_facility_ids = select(HistoricalFacility.id).where(
                    HistoricalFacility.history_id > last_facility_version_id
                )
                # We use an dictionary comprehension so that we can load
                # all the data and exit the transaction as soon as possible
                latest_facility_dedupe_records = {
                    f['id']: facility_values_to_dedupe_record(f)
                    for f in
                    transform_to_dict(session.query(Facility.id, Facility.country_code, Facility.name, Facility.address). \
                        filter(Facility.id.in_(changed_facility_ids)))
                }

            return facility_changes, latest_facility_dedupe_records

    @classmethod
    def _get_new_match_history(cls) -> MatchHistory:
        match_changes = []
        latest_match_records = {}
        latest_matched_facility_dedupe_records = {}
        with get_session() as session:
            db_match_version = session.query(
                func.max(HistoricalFacilityMatch.history_id)
            ).scalar()

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
                        HistoricalFacilityMatch.history_id > last_match_version_id
                    ). \
                    order_by(HistoricalFacilityMatch.history_id.asc())
                )

                # `FacilityMatch` rows are selected by match id. The port
                # filtered on `history_id` instead, which is the surrogate key
                # of the history table and belongs to a different sequence, so
                # the `latest_match_records[item['id']]` lookup in
                # `get_latest` never resolved and no confirmed match was ever
                # indexed incrementally. As above, the ids go in as subqueries
                # rather than as one bind parameter per backlog row.
                changed_match_ids = select(HistoricalFacilityMatch.id).where(
                    HistoricalFacilityMatch.history_id > last_match_version_id
                )
                # We use an dictionary comprehension so that we can load
                # all the data and exit the transaction as soon as possible.
                # `record` is the contributor's submitted spelling, joined
                # from `FacilityListItem`, because that is what
                # `get_canonical_items` indexes under the synthetic
                # `<facility>_MATCH-<id>` id when the model is trained. The
                # alternative spelling is the entire reason the synthetic id
                # exists; re-keying the facility's own values under it, as
                # this path used to, adds a duplicate of the plain facility
                # record and no new matching signal, and leaves a cold start
                # and an incremental refresh holding different indexes for
                # the same match.
                latest_match_records = {
                    m['id']: {
                        'facility': m['facility_id'],
                        'status': m['status'],
                        'is_active': m['is_active'],
                        'record': facility_values_to_dedupe_record({
                            'id': match_detail_to_extended_facility_id(
                                str(m['facility_id']), str(m['id'])
                            ),
                            'country': m['country_code'],
                            'name': m['name'],
                            'address': m['address'],
                        }),
                    } for m in session.query(FacilityMatch.id,
                                             FacilityMatch.facility_id,
                                             FacilityMatch.status,
                                             FacilityMatch.is_active,
                                             FacilityListItem.country_code,
                                             FacilityListItem.name,
                                             FacilityListItem.address). \
                        join(
                            FacilityListItem,
                            FacilityListItem.id ==
                            FacilityMatch.facility_list_item_id
                        ). \
                        filter(
                            FacilityMatch.id.in_(changed_match_ids)
                        )
                }

                # The facilities the *live* matches point at. A merge can
                # reassign `FacilityMatch.facility_id`, in which case the
                # history row still carries the old one.
                matched_facility_ids = select(FacilityMatch.facility_id).where(
                    FacilityMatch.id.in_(changed_match_ids)
                )
                # We use an dictionary comprehension so that we can load
                # all the data and exit the transaction as soon as possible.
                # Only the four columns `transform_to_dict` reads are
                # selected; loading whole `Facility` entities would pull the
                # PostGIS geometry column into the identity map for every
                # facility in the backlog.
                latest_matched_facility_dedupe_records = {
                    f['id']: facility_values_to_dedupe_record(f) for f in
                    transform_to_dict(session.query(Facility.id, Facility.country_code, Facility.name, Facility.address). \
                        filter(Facility.id.in_(matched_facility_ids)))
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

            for item in match_changes:
                match = (latest_match_records[item['id']]
                         if item['id'] in latest_match_records
                         else None)
                # The history row carries the facility the match pointed at
                # when it was written, which a later merge may have changed,
                # so the live value from `latest_match_records` is the one
                # checked here and the one the synthetic id is built from.
                has_facility = (
                    match is not None
                    and match['facility'] in
                    latest_matched_facility_dedupe_records)
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
                            record = match['record']
                            logger.debug(f'Indexing match {record}')
                            cls._gazetter.index(record)
                cls._match_version = item['history_id']

        except Exception as e:
            logger.error(f'[Matching] Get latest Gazetteer Error: {e}')

            try_reporting_error_to_rollbar(extra_data={
                'last_successful_facility_version': cls._facility_version,
                'last_successful_match_version': cls._match_version
            })
            raise e

        return cls._gazetter
