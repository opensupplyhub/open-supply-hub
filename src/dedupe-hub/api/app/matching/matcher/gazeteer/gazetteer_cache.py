import logging
from typing import Dict, List, Set, Tuple, Union
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
    List[HistoricalFacilityMatch], LatestMatchRecords, Set[str]
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
        # The markers get their own short-lived session: training takes
        # minutes, and holding this one open around it would leave a
        # connection `idle in transaction` on the primary throughout. Read
        # before training, so rows written during it are replayed next
        # refresh rather than skipped.
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
                # A Query re-issues its statement on every iteration, so it
                # is materialized once. The result set is now the whole
                # backlog, and a second pass would also read a different
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
                if not facility_changes:
                    # The marker can end up ahead of the table: a restored
                    # anonymized dump restarts the sequence lower. Left
                    # unreconciled, the guard stays true on a permanently
                    # empty backlog and the cache stops indexing for good.
                    # Logged because reconciling also means the rows below
                    # the marker are never indexed by this task.
                    logger.warning(
                        'Facility marker %s is ahead of the table; '
                        'reconciling to %s',
                        cls._facility_version, db_facility_version)
                    cls._facility_version = db_facility_version

                # A subquery rather than a list of bind parameters: one
                # parameter per backlog row would meet PostgreSQL's 65535
                # limit, which `get_latest` re-raises rather than degrades.
                changed_facility_ids = select(HistoricalFacility.id).where(
                    HistoricalFacility.history_id > last_facility_version_id
                )
                # We use an dictionary comprehension so that we can load
                # all the data and exit the transaction as soon as possible.
                # Candidates (OSDEV-3243) are left out, so a new or updated
                # candidate is never indexed; a candidate that graduates
                # (is_candidate -> false) shows up in history and is indexed
                # on that refresh like any other facility.
                latest_facility_dedupe_records = {
                    f['id']: facility_values_to_dedupe_record(f)
                    for f in
                    transform_to_dict(session.query(Facility.id, Facility.country_code, Facility.name, Facility.address). \
                        filter(
                            Facility.id.in_(changed_facility_ids),
                            Facility.is_candidate.is_(False),
                        ))
                }

            return facility_changes, latest_facility_dedupe_records

    @classmethod
    def _get_new_match_history(cls) -> MatchHistory:
        match_changes = []
        latest_match_records = {}
        existing_facility_ids = set()
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
                # the transaction as soon as possible.
                # `HistoricalFacilityMatch.facility_id` is deliberately not
                # selected: it records the facility as of the history row,
                # which a merge may since have reassigned. The live value
                # from `latest_match_records` is used instead.
                match_changes = list(
                    session.query(
                    HistoricalFacilityMatch.id, 
                    HistoricalFacilityMatch.history_type, 
                    HistoricalFacilityMatch.history_id
                    ). \
                    filter(
                        HistoricalFacilityMatch.history_id > last_match_version_id
                    ). \
                    order_by(HistoricalFacilityMatch.history_id.asc())
                )
                if not match_changes:
                    # See the note on the facility marker above.
                    logger.warning(
                        'Match marker %s is ahead of the table; '
                        'reconciling to %s',
                        cls._match_version, db_match_version)
                    cls._match_version = db_match_version

                # Selected by match id. Filtering on `history_id` — the
                # history table's own surrogate key, from a different
                # sequence — made the `latest_match_records[item['id']]`
                # lookup in `get_latest` miss every row, so no confirmed
                # match was ever indexed.
                changed_match_ids = select(HistoricalFacilityMatch.id).where(
                    HistoricalFacilityMatch.history_id > last_match_version_id
                )
                # We use an dictionary comprehension so that we can load
                # all the data and exit the transaction as soon as possible.
                # `record` is the contributor's submitted spelling, which
                # is what `get_canonical_items` indexes under the synthetic
                # `<facility>_MATCH-<id>` id at train time. The facility's
                # own values there would just duplicate its plain record.
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
                            FacilityMatch.id.in_(changed_match_ids),
                            # Only a confirmed match can be indexed, and
                            # the backlog is mostly AUTOMATIC rows after a
                            # large upload. Mirrors `get_canonical_items`.
                            FacilityMatch.status == FacilityMatch.CONFIRMED,
                        )
                }

                # The facilities the live matches point at; a merge can
                # reassign `FacilityMatch.facility_id`.
                matched_facility_ids = select(FacilityMatch.facility_id).where(
                    FacilityMatch.id.in_(changed_match_ids),
                    FacilityMatch.status == FacilityMatch.CONFIRMED,
                )
                # Only membership is tested in `get_latest`; the record it
                # indexes comes from `latest_match_records`. A candidate
                # (OSDEV-3243) does not count as an existing facility here,
                # so no match record pointing at one is ever indexed.
                existing_facility_ids = {
                    row.id for row in
                    session.query(Facility.id).filter(
                        Facility.id.in_(matched_facility_ids),
                        Facility.is_candidate.is_(False),
                    )
                }

            return (match_changes, latest_match_records,
                    existing_facility_ids)

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
             existing_facility_ids) = \
                cls._get_new_match_history()

            for item in match_changes:
                match = (latest_match_records[item['id']]
                         if item['id'] in latest_match_records
                         else None)
                # The live facility, not the history row's: a merge may
                # have reassigned it since.
                has_facility = (
                    match is not None
                    and match['facility'] in existing_facility_ids)
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
