import requests
from .base_production_locations_test \
    import BaseProductionLocationsTest


class ProductionLocationsTest(BaseProductionLocationsTest):

    def test_production_locations_status(self):
        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/",
            headers=self.basic_headers,
        )
        self.assertEqual(response.status_code, 200)

    def test_production_locations_exact(self):
        # Index a document
        doc = {
            "sector": [
                "Apparel"
            ],
            "address": "Vill. B.K. Bari, Taltoli, P.O.: Mirzapur Gazipur",
            "name": "Silver Composite Textile Mills Ltd.",
            "country": {
                "alpha_2": "BD"
            },
            "os_id": "BD2020052SV22HT",
            "coordinates": {
                "lon": 90.378162,
                "lat": 24.1166236
            },
            "claim_status": "unclaimed"
        }
        self.open_search_client.index(
            index=self.index_name,
            body=doc,
            id=self.open_search_client.count()
        )
        self.open_search_client.indices.refresh(
            index=self.index_name
        )

        search_name = "Silver%20Composite%20Textile%20Mills%20Ltd."
        query = "?size=1&name={}&sort_by=name&order_by=asc".\
            format(search_name)

        response = requests.get(
                f"{self.root_url}/api/v1/production-locations/{query}",
                headers=self.basic_headers,
            )

        result = response.json()
        self.assertEqual(result['data'][0]['os_id'], 'BD2020052SV22HT')
