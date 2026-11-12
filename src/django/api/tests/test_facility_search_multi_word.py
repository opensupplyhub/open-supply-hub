from api.models import (
    Contributor,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.models.facility.facility_manager_index_new import (
    FacilityIndexNewManager,
)

from django.contrib.gis.geos import Point
from django.http import QueryDict
from django.test import TestCase


class FacilitySearchMultiWordTest(TestCase):
    """
    A free-text search matches names that contain every typed word.

    Covers the ``q`` parameter on the search results, download and API
    paths, all of which filter through ``FacilityIndex``.
    """

    NAMES = (
        "Interloop Limited (Hosiery Division I)",
        "Interloop Limited Apparel Park",
        "Shahi Exports Pvt Ltd. Unit-07",
        "Shahi Exports Pvt Ltd Unit 36",
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

    def search(self, query):
        params = QueryDict("", mutable=True)
        params["q"] = query
        result = FacilityIndexNewManager.filter_by_query_params(self, params)
        return sorted(facility.name for facility in result)

    def assert_search(self, query, expected):
        self.assertEqual(
            sorted(expected),
            self.search(query),
            "unexpected results for {}".format(query),
        )

    def test_words_match_out_of_order(self):
        self.assert_search(
            "Interloop Hosiery",
            ["Interloop Limited (Hosiery Division I)"],
        )

    def test_words_match_with_text_between_them(self):
        self.assert_search(
            "Interloop Apparel",
            ["Interloop Limited Apparel Park"],
        )

    def test_unit_number_matches(self):
        self.assert_search(
            "shahi exports 07",
            ["Shahi Exports Pvt Ltd. Unit-07"],
        )

    def test_single_word_still_matches_every_name_containing_it(self):
        self.assert_search(
            "Interloop",
            [
                "Interloop Limited (Hosiery Division I)",
                "Interloop Limited Apparel Park",
            ],
        )

    def test_whole_string_match_is_preserved(self):
        # The old filter's exact-substring behavior is a subset of the new
        # one, so anything it matched still matches.
        self.assert_search(
            "Shahi Exports Pvt Ltd. Unit-07",
            ["Shahi Exports Pvt Ltd. Unit-07"],
        )

    def test_every_word_must_match(self):
        # Tokens are ANDed, so an extra word narrows rather than broadens.
        self.assert_search("Interloop Shahi", [])

    def test_blank_query_does_not_error(self):
        self.assertEqual([], self.search("   "))

    def test_misspelling_still_returns_nothing(self):
        # Tokenization is not fuzziness. Typo tolerance needs OpenSearch or
        # a trigram index; this records the current boundary.
        self.assert_search("Interlop", [])
