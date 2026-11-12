from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.models.facility.facility_index import FacilityIndex
from api.models.facility.facility_manager_index_new import (
    FacilityIndexNewManager,
)

from django.contrib.gis.geos import Point
from django.http import QueryDict
from django.test import TestCase


class FacilityNameSearchIndexTest(TestCase):
    """
    The free-text filter stays matched to the trigram index of 0269.

    Django's own ``__unaccent`` emits the STABLE ``unaccent()``, which
    cannot be indexed, so a refactor back to it would silently return the
    search to a sequential scan of every production location.
    """

    NAMES = (
        "OZEN AYBA TEKSTIL",
        "ÖZEN DÜĞME SAN VE TURZ.TİC LTD ŞT",
        "Interloop Limited (Hosiery Division I)",
    )

    def setUp(self):
        self.user = User.objects.create(email="example@example.com")
        self.user.set_password("password")
        self.user.save()

        self.contrib = Contributor.objects.create(
            admin=self.user,
            name="contributor name",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.list = FacilityList.objects.create(
            header="header", file_name="one", name="list_one"
        )

        self.source = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contrib,
        )

        for row_index, name in enumerate(self.NAMES):
            list_item = FacilityListItem.objects.create(
                name=name,
                address="address",
                country_code="US",
                sector=["Apparel"],
                row_index=row_index,
                status=FacilityListItem.CONFIRMED_MATCH,
                source=self.source,
            )
            Facility.objects.create(
                name=name,
                address="Address",
                country_code="US",
                location=Point(0, 0),
                created_from=list_item,
            )

    @staticmethod
    def query_sql(query):
        params = QueryDict("", mutable=True)
        params["q"] = query
        return str(
            FacilityIndexNewManager.filter_by_query_params(
                FacilityIndex.objects, params
            ).values("id").query
        )

    def search(self, query):
        params = QueryDict("", mutable=True)
        params["q"] = query
        result = FacilityIndexNewManager.filter_by_query_params(self, params)
        return sorted(facility.name for facility in result)

    def test_filter_folds_accents_through_immutable_unaccent(self):
        sql = self.query_sql("shahi")
        self.assertIn("public.immutable_unaccent", sql)

    def test_filter_does_not_use_the_unindexable_unaccent(self):
        # `UNACCENT(` with a word boundary before it; immutable_unaccent
        # contains the same word and must not be matched here.
        sql = self.query_sql("shahi").upper()
        self.assertNotIn(" UNACCENT(", sql)
        self.assertNotIn("(UNACCENT(", sql)

    def test_the_search_term_is_folded_too(self):
        # A one-sided transform would compare a folded column against an
        # unfolded term, so "özen" would stop matching "OZEN".
        sql = self.query_sql("özen")
        self.assertGreaterEqual(sql.count("public.immutable_unaccent"), 2)

    def test_every_token_is_folded(self):
        sql = self.query_sql("interloop hosiery")
        self.assertGreaterEqual(sql.count("public.immutable_unaccent"), 4)

    def test_unaccented_query_matches_accented_name(self):
        self.assertIn(
            "ÖZEN DÜĞME SAN VE TURZ.TİC LTD ŞT", self.search("ozen dugme")
        )

    def test_accented_query_matches_unaccented_name(self):
        self.assertIn("OZEN AYBA TEKSTIL", self.search("özen ayba"))

    def test_multi_word_match_is_preserved(self):
        self.assertEqual(
            ["Interloop Limited (Hosiery Division I)"],
            self.search("Interloop Hosiery"),
        )
