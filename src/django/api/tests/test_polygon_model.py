from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point
from django.db import IntegrityError, transaction
from django.test import TestCase

from api.models import Contributor, Polygon, User
from api.models.facility.facility_index import FacilityIndex

SQUARE_WKT = 'POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))'
SQUARE_WITH_HOLE_WKT = (
    'POLYGON((0 0, 0 10, 10 10, 10 0, 0 0), (2 2, 2 4, 4 4, 4 2, 2 2))'
)
OTHER_SQUARE_WKT = 'POLYGON((20 20, 20 30, 30 30, 30 20, 20 20))'


class PolygonModelTest(TestCase):
    """Tests for the Polygon model and its production-location query."""
    def setUp(self):
        self.user = User.objects.create(email='test@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='Test Contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

    def _make_facility(
        self, facility_id, lon, lat, country_code='US', sector=None,
        product_type=None,
    ):
        """Create a minimal FacilityIndex row at the given lon/lat."""
        return FacilityIndex.objects.create(
            id=facility_id,
            name='Test Facility',
            address='123 Main St',
            country_code=country_code,
            sector=sector or [],
            product_type=product_type or [],
            location=Point(lon, lat),
            contributors_count=1,
            contributors_id=[self.contributor.id],
            contributors=[{'id': self.contributor.id, 'name': 'Test'}],
            contrib_types=[Contributor.OTHER_CONTRIB_TYPE],
            facility_addresses=[{'address': '123 Main St'}],
            extended_fields=[],
            lists=[],
            approved_claim_ids=[],
            facility_names=[],
        )

    def test_facilities_respects_holes(self):
        """Locations inside a hole in the boundary are excluded."""
        polygon = Polygon.objects.create(
            name='square_with_hole',
            description='A square boundary with a hole cut out.',
            geom=MultiPolygon(GEOSGeometry(SQUARE_WITH_HOLE_WKT)),
        )
        inside = self._make_facility('US1000000INSD', 1, 1)
        in_hole = self._make_facility('US1000000HOLE', 3, 3)
        outside = self._make_facility('US1000000OUTS', 50, 50)

        result_ids = set(
            polygon.get_production_locations()
            .values_list('id', flat=True)
        )

        self.assertIn(inside.id, result_ids)
        self.assertNotIn(in_hole.id, result_ids)
        self.assertNotIn(outside.id, result_ids)

    def test_facilities_matches_any_part_of_a_multipolygon(self):
        """A location inside any disjoint part of the boundary matches."""
        polygon = Polygon.objects.create(
            name='two_disjoint_squares',
            description='A multipolygon made of two separate squares.',
            geom=MultiPolygon(
                GEOSGeometry(SQUARE_WKT), GEOSGeometry(OTHER_SQUARE_WKT)
            ),
        )
        in_first = self._make_facility('US1000000FRST', 1, 1)
        in_second = self._make_facility('US1000000SCND', 25, 25)
        outside = self._make_facility('US1000000OUTS', 50, 50)

        result_ids = set(
            polygon.get_production_locations()
            .values_list('id', flat=True)
        )

        self.assertIn(in_first.id, result_ids)
        self.assertIn(in_second.id, result_ids)
        self.assertNotIn(outside.id, result_ids)

    def _make_square_polygon(self):
        """Create a simple square Polygon to query against."""
        return Polygon.objects.create(
            name='square',
            description='A simple square boundary.',
            geom=MultiPolygon(GEOSGeometry(SQUARE_WKT)),
        )

    def test_country_filter_narrows_results(self):
        """The country filter keeps only matching countries, any case."""
        polygon = self._make_square_polygon()
        in_us = self._make_facility('US1000000USIN', 1, 1, country_code='US')
        in_india = self._make_facility(
            'IN1000000ININ', 2, 2, country_code='IN'
        )

        result_ids = set(
            polygon.get_production_locations(
                # Lowercase on purpose: country codes are normalized.
                filters={'country': ['in']}
            ).values_list('id', flat=True)
        )

        self.assertIn(in_india.id, result_ids)
        self.assertNotIn(in_us.id, result_ids)

    def test_sector_filter_matches_overlapping_values(self):
        """The sector filter matches on any of a location's sectors."""
        polygon = self._make_square_polygon()
        apparel = self._make_facility(
            'US1000000APPL', 1, 1, sector=['Apparel', 'Textiles']
        )
        food = self._make_facility(
            'US1000000FOOD', 2, 2, sector=['Food & Beverage']
        )

        result_ids = set(
            polygon.get_production_locations(
                filters={'sector': ['Apparel']}
            ).values_list('id', flat=True)
        )

        self.assertIn(apparel.id, result_ids)
        self.assertNotIn(food.id, result_ids)

    def test_filters_combine_with_and_semantics(self):
        """Separate filter keys must all hold at once (AND semantics)."""
        polygon = self._make_square_polygon()
        match = self._make_facility(
            'IN1000000BOTH', 1, 1, country_code='IN', sector=['Apparel']
        )
        wrong_sector = self._make_facility(
            'IN1000000SCTR', 2, 2, country_code='IN', sector=['Mining']
        )

        result_ids = set(
            polygon.get_production_locations(
                filters={'country': ['IN'], 'sector': ['Apparel']}
            ).values_list('id', flat=True)
        )

        self.assertIn(match.id, result_ids)
        self.assertNotIn(wrong_sector.id, result_ids)

    def test_unknown_filter_field_raises(self):
        """A typo in a filter key raises instead of silently unfiltering."""
        polygon = self._make_square_polygon()

        with self.assertRaises(ValueError) as ctx:
            polygon.get_production_locations(filters={'contry': ['US']})

        self.assertIn('contry', str(ctx.exception))

    def test_polygon_filters_follow_the_shared_zone_set_rules(self):
        """A filter means the same thing on a polygon as on a zone set,
        because both go through the shared helper: product types are
        matched without regard to capitals (the index stores them in
        lower case), whereas `sugar` is a different product from
        `sugarcane`."""
        polygon = self._make_square_polygon()
        cane = self._make_facility(
            'US1000000CANE', 1, 1, product_type=['sugar cane']
        )
        sugar = self._make_facility(
            'US1000000SUGR', 2, 2, product_type=['sugarcane']
        )

        def ids(filters):
            return set(
                polygon.get_production_locations(filters=filters)
                .values_list('id', flat=True)
            )

        self.assertEqual(ids({'product_type': ['Sugar Cane']}), {cane.id})
        self.assertEqual(ids({'product_type': ['SUGARCANE']}), {sugar.id})
        self.assertEqual(ids({'product_type': ['sugar']}), set())

    def test_unusable_filters_are_refused_like_on_zone_sets(self):
        """An empty list, a blank value, or too many values raises
        instead of quietly matching nothing."""
        polygon = self._make_square_polygon()
        cases = (
            {'sector': []},
            {'sector': ['Apparel', '  ']},
            {'sector': [f'sector {i}' for i in range(201)]},
        )
        for filters in cases:
            with self.subTest(filters=str(filters)[:40]):
                with self.assertRaises(ValueError):
                    polygon.get_production_locations(filters=filters)

    def test_no_filters_means_every_location_inside(self):
        """`None` and `{}` apply no filtering."""
        polygon = self._make_square_polygon()
        inside = self._make_facility('US1000000NOFL', 1, 1)
        for filters in (None, {}):
            ids = set(
                polygon.get_production_locations(filters=filters)
                .values_list('id', flat=True)
            )
            self.assertIn(inside.id, ids)

    def test_polygon_names_must_be_unique(self):
        """The database refuses a second polygon with the same name."""
        # (kept as a database-level backstop; the admin form catches
        # duplicates earlier with a friendly message)
        self._make_square_polygon()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._make_square_polygon()

    def test_polygons_get_a_unique_uuid_on_creation(self):
        """Every polygon is assigned a UUID automatically, for joins."""
        first = self._make_square_polygon()
        second = Polygon.objects.create(
            name='other_square',
            description='A second boundary.',
            geom=first.geom,
        )

        self.assertIsNotNone(first.uuid)
        self.assertIsNotNone(second.uuid)
        self.assertNotEqual(first.uuid, second.uuid)
