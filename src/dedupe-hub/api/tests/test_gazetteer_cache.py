import unittest
from operator import gt
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from sqlalchemy.sql import operators

from app.database.models.facility_list_item import FacilityListItem
from app.database.models.facility_match import FacilityMatch
from app.database.models.historical_facility import HistoricalFacility
from app.matching.matcher.gazeteer.gazetteer_cache import GazetteerCache

MODULE = 'app.matching.matcher.gazeteer.gazetteer_cache'


class Row:
    """
    Stands in for the SQLAlchemy ``LegacyRow`` the production queries return,
    which supports both ``row.id`` and ``row['id']``. A plain dict skips the
    attribute path, which is how a broken branch stays green.
    """

    def __init__(self, **values):
        self.__dict__.update(values)

    def __getitem__(self, key):
        return self.__dict__[key]


class TestGazetteerCacheIncrementalIndex(unittest.TestCase):
    """
    `GazetteerCache` holds one trained Gazetteer in memory for the life of the
    process and is expected to index every `Facility` added since the previous
    call to `get_latest`.

    A regression here is silent in production: the gazetteer keeps matching
    against a stale index, the match simply misses, and a duplicate OS ID is
    minted instead. So the incremental path is pinned down explicitly.
    """

    def setUp(self):
        self._reset_cache()

    def tearDown(self):
        self._reset_cache()

    @staticmethod
    def _reset_cache():
        GazetteerCache._gazetter = None
        GazetteerCache._facility_version = None
        GazetteerCache._match_version = None

    @staticmethod
    def _facility_change(facility_id, history_id, history_type='+'):
        return {
            'id': facility_id,
            'country': 'US',
            'name': 'Facility {}'.format(facility_id),
            'address': '{} Main St'.format(history_id),
            'history_type': history_type,
            'history_id': history_id,
        }

    @staticmethod
    def _match_row(match_id, facility_id, history_id, history_type='+'):
        return Row(
            id=match_id,
            facility_id=facility_id,
            history_type=history_type,
            history_id=history_id,
        )

    @staticmethod
    def _run_facility_history(db_max, rows=None):
        """
        Drives `_get_new_facility_history` against mocks for the three
        queries it issues, and hands back the mocks worth asserting on.
        """
        q = SimpleNamespace(
            ordered=MagicMock(), history=MagicMock(),
            filtered=MagicMock(), facility=MagicMock(), session=MagicMock())
        q.ordered.all.return_value = rows or []
        q.history.order_by.return_value = q.ordered
        q.filtered.filter.return_value = q.history
        q.facility.filter.return_value = []
        q.session.query.side_effect = [
            MagicMock(**{'scalar.return_value': db_max}),
            q.filtered,
            q.facility,
        ]
        with patch('{}.get_session'.format(MODULE)) as get_session:
            get_session.return_value.__enter__.return_value = q.session
            GazetteerCache._get_new_facility_history()
        return q

    @staticmethod
    def _normalized_sql(expression):
        return ' '.join(str(expression).split())

    def test_fetches_all_history_after_the_marker(self):
        """
        The history query must select everything *newer than* the marker. An
        equality filter returns a single row, which silently caps the cache at
        one facility per refresh.
        """
        GazetteerCache._facility_version = 100
        q = self._run_facility_history(db_max=102)

        # the comparison handed to .filter() must be `history_id > marker`
        expr = q.filtered.filter.call_args[0][0]
        self.assertIs(expr.operator, gt)
        self.assertEqual(expr.left.name, 'history_id')
        self.assertEqual(
            expr.left.table.name, HistoricalFacility.__tablename__
        )
        self.assertEqual(expr.right.value, 100)

        # oldest-first, so the marker ends on the newest row
        order_expr = q.history.order_by.call_args[0][0]
        self.assertIs(order_expr.modifier, operators.asc_op)

    def test_indexes_every_new_facility_not_just_one(self):
        """The N>=2 regression: all new facilities reach the index."""
        changes = [
            self._facility_change('US1', 101),
            self._facility_change('US2', 102),
            self._facility_change('US3', 103),
        ]
        records = {
            'US1': {'US1': {'country': 'us', 'name': 'a', 'address': 'a'}},
            'US2': {'US2': {'country': 'us', 'name': 'b', 'address': 'b'}},
            'US3': {'US3': {'country': 'us', 'name': 'c', 'address': 'c'}},
        }
        gazetteer = MagicMock()
        GazetteerCache._gazetter = gazetteer

        with patch.object(
            GazetteerCache, '_get_new_facility_history',
            return_value=(changes, records)
        ), patch.object(
            GazetteerCache, '_get_new_match_history',
            return_value=([], {}, set())
        ):
            GazetteerCache.get_latest()

        self.assertEqual(gazetteer.index.call_count, 3)
        indexed = [call[0][0] for call in gazetteer.index.call_args_list]
        self.assertEqual(
            [list(record.keys())[0] for record in indexed],
            ['US1', 'US2', 'US3']
        )

    def test_marker_advances_to_the_newest_history_id(self):
        """
        The marker must end on the newest row processed, otherwise the next
        refresh re-reads history it has already indexed.
        """
        changes = [
            self._facility_change('US1', 101),
            self._facility_change('US2', 102),
            self._facility_change('US3', 103),
        ]
        GazetteerCache._gazetter = MagicMock()

        with patch.object(
            GazetteerCache, '_get_new_facility_history',
            return_value=(changes, {})
        ), patch.object(
            GazetteerCache, '_get_new_match_history',
            return_value=([], {}, set())
        ):
            GazetteerCache.get_latest()

        self.assertEqual(GazetteerCache._facility_version, 103)

    def test_match_marker_advances_past_unconfirmed_rows(self):
        """
        The match marker records how far through the history we have *read*,
        not what we chose to index. Advancing it only for confirmed matches
        strands it at the last CONFIRMED row, so every later refresh re-reads
        a growing tail of history.
        """
        match_changes = [
            self._match_row(match_id=1, facility_id='US1', history_id=201),
            self._match_row(match_id=2, facility_id='US2', history_id=202),
        ]
        GazetteerCache._gazetter = MagicMock()

        with patch.object(
            GazetteerCache, '_get_new_facility_history',
            return_value=([], {})
        ), patch.object(
            GazetteerCache, '_get_new_match_history',
            # no confirmed matches among the new rows
            return_value=(match_changes, {}, {})
        ):
            GazetteerCache.get_latest()

        self.assertEqual(GazetteerCache._match_version, 202)

    def test_rebuild_stores_executed_version_markers(self):
        """
        The markers must be executed scalars. Storing the unexecuted Query
        makes every later comparison against them meaningless.
        """
        session = MagicMock()
        session.query.side_effect = [
            MagicMock(**{'scalar.return_value': 7}),
            MagicMock(**{'scalar.return_value': 9}),
        ]

        with patch('{}.get_session'.format(MODULE)) as get_session, \
                patch('{}.get_canonical_items'.format(MODULE),
                      return_value={'US1': {'name': 'a'}}), \
                patch('{}.get_messy_items_for_training'.format(MODULE),
                      return_value={}), \
                patch('{}.gazetteer_train'.format(MODULE),
                      return_value=MagicMock()):
            get_session.return_value.__enter__.return_value = session
            GazetteerCache._rebuild_gazetteer()

        self.assertEqual(GazetteerCache._facility_version, 7)
        self.assertEqual(GazetteerCache._match_version, 9)

    def test_match_records_are_keyed_by_match_id_not_history_id(self):
        """
        `latest_match_records` is read back by `FacilityMatch` id. Selecting
        those rows by `history_id`, from a different sequence, makes the
        lookup miss every row, so no confirmed match is ever indexed.
        """
        GazetteerCache._match_version = 200

        ordered = MagicMock()
        ordered.__iter__ = lambda self: iter([])
        match_q = MagicMock()
        match_q.order_by.return_value = ordered
        filtered = MagicMock()
        filtered.filter.return_value = match_q
        joined = MagicMock()
        joined.filter.return_value = []
        facility_match_q = MagicMock()
        facility_match_q.join.return_value = joined
        facility_q = MagicMock()
        facility_q.filter.return_value = []

        session = MagicMock()
        session.query.side_effect = [
            MagicMock(**{'scalar.return_value': 202}),
            filtered,
            facility_match_q,
            facility_q,
        ]

        with patch('{}.get_session'.format(MODULE)) as get_session:
            get_session.return_value.__enter__.return_value = session
            GazetteerCache._get_new_match_history()

        sql = self._normalized_sql(joined.filter.call_args[0][0])
        self.assertIn('api_facilitymatch.id IN', sql)
        self.assertIn('SELECT api_historicalfacilitymatch.id', sql)
        self.assertNotIn('SELECT api_historicalfacilitymatch.history_id', sql)

        # the submitted spelling is joined in from `FacilityListItem`, the
        # same source `get_canonical_items` uses at train time
        self.assertIs(
            facility_match_q.join.call_args[0][0], FacilityListItem
        )
        selected = self._normalized_sql(facility_q.filter.call_args[0][0])
        # the facility existence check follows the *live* match, not the
        # facility id recorded on the history row
        self.assertIn('SELECT api_facilitymatch.facility_id', selected)

    def test_confirmed_match_is_indexed(self):
        """
        Confirmed matches are indexed under a synthetic
        `<facility>_MATCH-<id>` id. This is the branch the wrong lookup key
        silently disabled.
        """
        match_changes = [
            self._match_row(match_id=11, facility_id='US1', history_id=201),
        ]
        submitted = {
            'US1_MATCH-11': {
                'country': 'us',
                'name': 'contributor spelling',
                'address': 'contributor address',
            }
        }
        latest_match_records = {
            11: {
                'facility': 'US1',
                'status': FacilityMatch.CONFIRMED,
                'is_active': True,
                'record': submitted,
            }
        }
        facilities = {
            'US1': {'US1': {'country': 'us', 'name': 'a', 'address': 'b'}}
        }
        gazetteer = MagicMock()
        GazetteerCache._gazetter = gazetteer

        with patch.object(
            GazetteerCache, '_get_new_facility_history',
            return_value=([], {})
        ), patch.object(
            GazetteerCache, '_get_new_match_history',
            return_value=(match_changes, latest_match_records, facilities)
        ):
            GazetteerCache.get_latest()

        # the contributor's spelling, not a re-keyed copy of the facility's
        # own values, which would add no new matching signal
        gazetteer.index.assert_called_once_with(submitted)
        self.assertEqual(GazetteerCache._match_version, 201)

    def test_facility_history_is_read_once(self):
        """
        The history query object is a `Query`; iterating it twice issues the
        statement twice and reads two different READ COMMITTED snapshots.
        With `>` restored that is the whole backlog, not one row.
        """
        GazetteerCache._facility_version = 100
        q = self._run_facility_history(db_max=102)

        q.ordered.all.assert_called_once_with()
        # the changed ids go in as a subquery, not one bind parameter per row
        sql = self._normalized_sql(q.facility.filter.call_args[0][0])
        self.assertIn('SELECT api_historicalfacility.id', sql)

    def test_rebuild_closes_the_marker_session_before_training(self):
        """
        `gazetteer_train` takes minutes. Reading the markers with `.scalar()`
        opens a real transaction, so training inside that block would leave a
        connection `idle in transaction` on the primary for the whole rebuild.
        """
        events = []

        session = MagicMock()
        session.query.side_effect = [
            MagicMock(**{'scalar.return_value': 7}),
            MagicMock(**{'scalar.return_value': 9}),
        ]
        session_cm = MagicMock()
        session_cm.__enter__.return_value = session
        session_cm.__exit__.side_effect = (
            lambda *args: events.append('session closed')
        )

        def train(*args, **kwargs):
            events.append('gazetteer trained')
            return MagicMock()

        with patch('{}.get_session'.format(MODULE),
                   return_value=session_cm), \
                patch('{}.get_canonical_items'.format(MODULE),
                      return_value={'US1': {'name': 'a'}}), \
                patch('{}.get_messy_items_for_training'.format(MODULE),
                      return_value={}), \
                patch('{}.gazetteer_train'.format(MODULE), side_effect=train):
            GazetteerCache._rebuild_gazetteer()

        self.assertEqual(events, ['session closed', 'gazetteer trained'])

    def test_marker_ahead_of_the_table_is_reconciled(self):
        """
        Restoring an anonymized dump under a running task restarts
        `history_id` below the in-memory marker. The guard then stays true
        while the backlog stays empty, and the cache stops indexing for good.
        """
        GazetteerCache._facility_version = 9000
        self._run_facility_history(db_max=120)

        self.assertEqual(GazetteerCache._facility_version, 120)


if __name__ == '__main__':
    unittest.main()
