import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import text

from app.config import settings
from app.database.models.facility import Facility
from app.database.models.facility_list_item import FacilityListItem
from app.database.models.facility_list_item_temp import FacilityListItemTemp
from app.database.models.facility_match import FacilityMatch
from app.database.models.facility_match_temp import FacilityMatchTemp
from app.database.models.source import Source
from app.database.modifier.extended_fields import (
    update_extendedfields_for_list_item,
)
from app.database.sqlalchemy import get_session
from app.matching.DTOs.facility_match_dto import FacilityMatchDTO
from app.matching.DTOs.item_update_dto import ItemUpdateDTO

log = logging.getLogger(__name__)


class Writer:
    """
    Writes the outcome of matching one item at a time, each in a single
    transaction: the Facility created for it (if any), its match rows, its
    extended fields and its final status.

    Django answers `POST /api/facilities/` by polling the list item's status
    and reading its matches as soon as the status is final. Committing the
    status before the matches, and the matches one row at a time, let that
    read return a partial set, e.g. `MATCHED` with the pending matches but
    not yet the automatic one, so no `os_id` (OSDEV-3149).

    The item row is locked and must still be `GEOCODED`, so an item is
    written at most once even if two dedupe-hub tasks process the same
    message (every task joins its own consumer group).
    """

    def __init__(self):
        pass

    def write(
        self,
        processed_data: List[FacilityMatchDTO],
        item_updates: Optional[Dict[int, ItemUpdateDTO]] = None
    ) -> List[FacilityMatchDTO]:
        item_updates = item_updates or {}

        matches_by_item: Dict[int, List[FacilityMatchDTO]] = {}
        for match in processed_data:
            matches_by_item.setdefault(
                int(match['facility_list_item_id']), []
            ).append(match)

        item_ids = list(matches_by_item.keys())
        item_ids.extend(
            item_id for item_id in item_updates
            if item_id not in matches_by_item
        )

        written: List[FacilityMatchDTO] = []
        for item_id in item_ids:
            matches = matches_by_item.get(item_id, [])
            if self._write_item(item_id, matches, item_updates.get(item_id)):
                written.extend(matches)

        if len(written) > 0 and settings.dedupe_hub_live:
            self._index_facilities(
                {match['facility_id'] for match in written}
            )

        return written

    def _write_item(
        self,
        item_id: int,
        matches: List[FacilityMatchDTO],
        update: Optional[ItemUpdateDTO]
    ) -> bool:
        with get_session() as session:
            status = session.query(FacilityListItemTemp.status). \
                filter(FacilityListItemTemp.id == item_id). \
                with_for_update(). \
                scalar()
            if status != FacilityListItemTemp.GEOCODED:
                log.warning(
                    f'[Matching] FacilityListItem {item_id} skipped: its '
                    f'status is {status}, so it has already been matched.'
                )
                session.rollback()
                return False

            write_origin = (
                settings.dedupe_hub_live and
                bool(session.query(Source.create).
                     join(FacilityListItem,
                          FacilityListItem.source_id == Source.id).
                     filter(FacilityListItem.id == item_id).
                     scalar())
            )

            if update and update.get('new_facility') and write_origin:
                session.add(self._make_facility(update['new_facility']))
                # Inserted before the rows that reference it.
                session.flush()

            now = datetime.now()
            for match in matches:
                session.add(self._make_match(FacilityMatchTemp(), match, now))
                if write_origin:
                    session.add(self._make_match(FacilityMatch(), match, now))

            if update:
                self._update_item(session, FacilityListItemTemp, update)
                if write_origin:
                    self._update_item(session, FacilityListItem, update)
                    if update['facility_id'] is not None:
                        update_extendedfields_for_list_item(
                            session, item_id, update['facility_id']
                        )

            session.commit()
            return True

    @staticmethod
    def _make_facility(new_facility) -> Facility:
        facility = Facility()
        facility.id = new_facility['id']
        facility.name = new_facility['name']
        facility.address = new_facility['address']
        facility.country_code = new_facility['country_code']
        facility.location = new_facility['location']
        facility.created_from_id = new_facility['created_from_id']
        facility.created_at = datetime.now()
        facility.updated_at = datetime.now()
        return facility

    @staticmethod
    def _make_match(facility_match, match: FacilityMatchDTO, now: datetime):
        facility_match.facility_id = match['facility_id']
        facility_match.confidence = float(match['confidence'])
        facility_match.facility_list_item_id = match['facility_list_item_id']
        facility_match.status = match['status']
        facility_match.results = match['results']
        if isinstance(facility_match, FacilityMatchTemp):
            facility_match.version = settings.dedupe_hub_version
        facility_match.created_at = now
        facility_match.updated_at = now
        return facility_match

    @staticmethod
    def _update_item(session, list_item_type, update: ItemUpdateDTO) -> None:
        values = {
            'status': update['status'],
            'facility_id': update['facility_id'],
            'processing_results': update['processing_results'],
        }
        if list_item_type == FacilityListItemTemp:
            values['version'] = settings.dedupe_hub_version
        session.query(list_item_type). \
            filter(list_item_type.id == update['facility_list_item_id']). \
            update(values, synchronize_session=False)

    @staticmethod
    def _index_facilities(facility_ids) -> None:
        with get_session() as session:
            session.execute(
                text('call index_facilities_by(:data);'),
                {'data': list(facility_ids)}
            )
            session.commit()
