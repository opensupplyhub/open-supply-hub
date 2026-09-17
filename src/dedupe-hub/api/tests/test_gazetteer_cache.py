import unittest
from operator import gt
from unittest.mock import MagicMock, patch

from sqlalchemy.sql import operators

from app.database.models.historical_facility import HistoricalFacility
from app.matching.matcher.gazeteer.gazetteer_cache import GazetteerCache

MODULE = 'app.matching.matcher.gazeteer.gazetteer_cache'


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

    def test_fetches_all_history_after_the_marker(self):
        """
        The history query must select everything *newer than* the marker. An
        equality filter returns a single row, which silently caps the cache at
        one facility per refresh.
        """
        GazetteerCache._facility_version = 100

        history_q = MagicMock()
        history_q.order_by.return_value = []
        filtered = MagicMock()
        filtered.filter.return_value = history_q
        facility_q = MagicMock()
        facility_q.filter.return_value = []

        session = MagicMock()
        session.query.side_effect = [
            MagicMock(**{'scalar.return_value': 102}),
            filtered,
            facility_q,
        ]

        with patch('{}.get_session'.format(MODULE)) as get_session:
            get_session.return_value.__enter__.return_value = session
            GazetteerCache._get_new_facility_history()

        # the comparison handed to .filter() must be `history_id > marker`
        expr = filtered.filter.call_args[0][0]
        self.assertIs(expr.operator, gt)
        self.assertEqual(expr.left.name, 'history_id')
        self.assertEqual(
            expr.left.table.name, HistoricalFacility.__tablename__
        )
        self.assertEqual(expr.right.value, 100)

        # oldest-first, so the marker ends on the newest row
        order_expr = history_q.order_by.call_args[0][0]
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
            return_value=([], {}, {})
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
            return_value=([], {}, {})
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
            {'id': 1, 'facility_id': 'US1', 'history_type': '+',
             'history_id': 201},
            {'id': 2, 'facility_id': 'US2', 'history_type': '+',
             'history_id': 202},
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


if __name__ == '__main__':
    unittest.main()
