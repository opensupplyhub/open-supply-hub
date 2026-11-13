import json

from api.models import (
    Contributor,
    EmbedConfig,
    EmbedSupplyChain,
    Facility,
    FacilityListItem,
    Source,
    User,
)
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.gis.geos import Point


class EmbedSupplyChainsTest(APITestCase):
    """
    A contributor's supply chains for their embedded map: the contributor's
    own API, the checks on what they save, and what visitors are given.
    """
    url = "/api/embed-supply-chains/"
    password = "example123"

    def setUp(self):
        self.contributor = self._contributor("brand@example.com", "Brand")
        self.source = self._source(self.contributor)
        self.factory = self._facility("Factory", {"tier": "1"}, lng=10)
        self.mill = self._facility("Mill", {"tier": "2"}, lng=20)
        self.spinner = self._facility("Spinner", {"tier": "3"}, lng=30)

        self.other = self._contributor("other@example.com", "Other")
        self.other_source = self._source(self.other)
        self.foreign = self._facility(
            "Foreign Factory", {}, source=self.other_source
        )

    # ------------------------------------------------------------------ #
    # fixtures                                                            #
    # ------------------------------------------------------------------ #
    def _contributor(self, email, name, embed_level=3):
        user = User.objects.create(email=email)
        user.set_password(self.password)
        user.save()
        return Contributor.objects.create(
            admin=user,
            name=name,
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
            embed_level=embed_level,
            embed_config=EmbedConfig.objects.create(),
        )

    def _source(self, contributor):
        return Source.objects.create(
            source_type=Source.SINGLE,
            is_active=True,
            is_public=True,
            contributor=contributor,
        )

    def _facility(self, name, raw_json, source=None, lng=0):
        item = FacilityListItem.objects.create(
            name=name,
            address="1 Main Street",
            country_code="US",
            sector=["Apparel"],
            row_index=1,
            geocoded_point=Point(lng, 5),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source or self.source,
            raw_header="",
            raw_json=raw_json,
            raw_data=str(raw_json),
        )
        facility = Facility.objects.create(
            name=name,
            address="1 Main Street",
            country_code="US",
            created_from=item,
            location=Point(lng, 5),
        )
        item.facility = facility
        item.save()
        return facility

    def _login(self, email="brand@example.com"):
        self.client.login(email=email, password=self.password)

    def _chain(self, **overrides):
        data = {
            "name": "Insulated jacket",
            "description": "How our jacket is made.",
            "product_url": "https://example.com/jacket",
            "nodes": [
                {"os_id": self.factory.id, "stage": "Final assembly"},
                {"os_id": self.mill.id, "stage": "Material production"},
                {"os_id": self.spinner.id, "stage": "Raw material"},
            ],
            "links": [
                [self.mill.id, self.factory.id],
                [self.spinner.id, self.mill.id],
            ],
        }
        data.update(overrides)
        return data

    def _post(self, **overrides):
        return self.client.post(
            self.url, self._chain(**overrides), format="json"
        )

    def _public_chains(self):
        response = self.client.get(
            "/api/contributor-embed-configs/{}/".format(self.contributor.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return json.loads(response.content)["supply_chains"]

    # ------------------------------------------------------------------ #
    # who can use it                                                      #
    # ------------------------------------------------------------------ #
    def test_requires_login(self):
        self.assertIn(
            self.client.get(self.url).status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_requires_the_deluxe_embed_level(self):
        self.contributor.embed_level = 2
        self.contributor.save()
        self._login()

        self.assertEqual(
            status.HTTP_403_FORBIDDEN, self.client.get(self.url).status_code
        )
        self.assertEqual(status.HTTP_403_FORBIDDEN, self._post().status_code)

    def test_a_contributor_only_sees_their_own_chains(self):
        self._login()
        created = self._post()
        self.assertEqual(status.HTTP_201_CREATED, created.status_code)
        chain_id = json.loads(created.content)["id"]
        self.assertEqual(
            self.contributor,
            EmbedSupplyChain.objects.get(id=chain_id).contributor,
        )
        self.assertEqual(1, len(json.loads(self.client.get(self.url).content)))

        self.client.logout()
        self._login("other@example.com")
        self.assertEqual([], json.loads(self.client.get(self.url).content))
        detail = "{}{}/".format(self.url, chain_id)
        self.assertEqual(
            status.HTTP_404_NOT_FOUND, self.client.get(detail).status_code
        )
        self.assertEqual(
            status.HTTP_404_NOT_FOUND,
            self.client.patch(
                detail, {"name": "Taken over"}, format="json"
            ).status_code,
        )
        self.assertEqual(
            status.HTTP_404_NOT_FOUND, self.client.delete(detail).status_code
        )

    # ------------------------------------------------------------------ #
    # what can be saved                                                   #
    # ------------------------------------------------------------------ #
    def test_locations_must_be_the_contributors_own_facilities(self):
        self._login()
        response = self._post(
            nodes=[
                {"os_id": self.factory.id, "stage": ""},
                {"os_id": self.foreign.id, "stage": ""},
            ],
            links=[],
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertIn(self.foreign.id, response.content.decode())

    def test_links_cannot_loop(self):
        self._login()
        response = self._post(
            links=[
                [self.mill.id, self.factory.id],
                [self.spinner.id, self.mill.id],
                [self.factory.id, self.spinner.id],
            ]
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_links_must_join_locations_in_the_chain(self):
        self._login()
        for links in (
            [[self.mill.id, "US0000000000000"]],
            [[self.mill.id, self.mill.id]],
            [[self.mill.id]],
        ):
            with self.subTest(links=links):
                self.assertEqual(
                    status.HTTP_400_BAD_REQUEST,
                    self._post(links=links).status_code,
                )

    def test_a_location_can_only_be_in_a_chain_once(self):
        self._login()
        response = self._post(
            nodes=[
                {"os_id": self.factory.id, "stage": ""},
                {"os_id": self.factory.id, "stage": ""},
            ],
            links=[],
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_product_link_must_be_a_web_address(self):
        self._login()
        self.assertEqual(
            status.HTTP_400_BAD_REQUEST,
            self._post(product_url="javascript:alert(1)").status_code,
        )
        self.assertEqual(
            status.HTTP_201_CREATED, self._post(product_url="").status_code
        )

    def test_several_suppliers_can_feed_one_location(self):
        self._login()
        response = self._post(
            links=[
                [self.mill.id, self.factory.id],
                [self.spinner.id, self.factory.id],
            ]
        )

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_a_chain_can_be_published_without_resending_its_locations(self):
        self._login()
        chain_id = json.loads(self._post().content)["id"]

        response = self.client.patch(
            "{}{}/".format(self.url, chain_id),
            {"is_published": True},
            format="json",
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        chain = EmbedSupplyChain.objects.get(id=chain_id)
        self.assertTrue(chain.is_published)
        self.assertEqual(3, len(chain.nodes))

    # ------------------------------------------------------------------ #
    # what visitors get                                                   #
    # ------------------------------------------------------------------ #
    def test_visitors_only_get_published_chains(self):
        self._login()
        self._post(name="Draft")
        self._post(name="Live", is_published=True)
        self.client.logout()

        self.assertEqual(
            ["Live"], [chain["name"] for chain in self._public_chains()]
        )

    def test_published_chain_carries_each_locations_details(self):
        config = self.contributor.embed_config
        config.color_by_field = "tier"
        config.save()
        self._login()
        self._post(is_published=True)
        self.client.logout()

        chain = self._public_chains()[0]
        self.assertEqual("https://example.com/jacket", chain["product_url"])
        self.assertEqual(
            {
                "os_id": self.mill.id,
                "name": "Mill",
                "address": "1 Main Street",
                "country_name": "United States",
                "lat": 5.0,
                "lng": 20.0,
                "stage": "Material production",
                "tier": "2",
            },
            chain["nodes"][1],
        )
        self.assertEqual(
            [[self.mill.id, self.factory.id], [self.spinner.id, self.mill.id]],
            chain["links"],
        )

    def test_a_facility_that_no_longer_exists_drops_out_of_a_chain(self):
        self._login()
        chain_id = json.loads(self._post(is_published=True).content)["id"]
        self.client.logout()
        # Stored chains are not rechecked when a facility is later removed,
        # so write the stale location straight to the row.
        chain = EmbedSupplyChain.objects.get(id=chain_id)
        gone = "US0000000GONE00"
        chain.nodes = chain.nodes + [{"os_id": gone, "stage": "Raw material"}]
        chain.links = chain.links + [[gone, self.spinner.id]]
        chain.save()

        published = self._public_chains()[0]
        self.assertEqual(
            ["Factory", "Mill", "Spinner"],
            [node["name"] for node in published["nodes"]],
        )
        self.assertEqual(
            [[self.mill.id, self.factory.id], [self.spinner.id, self.mill.id]],
            published["links"],
        )
