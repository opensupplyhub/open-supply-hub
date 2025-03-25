import requests
from .base_api_test \
    import BaseAPITest


class ProductionLocationsTest(BaseAPITest):

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
            index=self.production_locations_index_name,
            body=doc,
            id=self.open_search_client.count()
        )
        self.open_search_client.indices.refresh(
            index=self.production_locations_index_name
        )

        search_name = "Silver Composite Textile Mills Ltd."
        query = f"?size=1&name={search_name}"

        response = requests.get(
                f"{self.root_url}/api/v1/production-locations/{query}",
                headers=self.basic_headers,
            )

        result = response.json()
        self.assertEqual(result['data'][0]['os_id'], 'BD2020052SV22HT')

    def test_production_locations_country(self):

        response = requests.get(
                f"{self.root_url}/api/v1/production-locations/",
                headers=self.basic_headers,
            )

        result = response.json()
        country = result['data'][0]['country']

        self.assertIsNotNone(country['name'])
        self.assertIsNotNone(country['alpha_2'])
        self.assertIsNotNone(country['alpha_3'])
        self.assertIsNotNone(country['numeric'])

    def test_production_locations_history_os_id(self):
        doc = {
            "sector": [
                "Apparel"
            ],
            "address": "Test Address",
            "name": "Test Name",
            "country": {
                "alpha_2": "US"
            },
            "os_id": "US2020052SV22HT",
            "historical_os_id": "US20203545HUE4L",
            "coordinates": {
                "lon": 90.378162,
                "lat": 24.1166236
            },
        }
        self.open_search_client.index(
            index=self.production_locations_index_name,
            body=doc,
            id=self.open_search_client.count()
        )
        self.open_search_client.indices.refresh(
            index=self.production_locations_index_name
        )

        search_os_id = "US2020052SV22HT"
        query = f"?size=1&os_id={search_os_id}"

        response = requests.get(
                f"{self.root_url}/api/v1/production-locations/{query}",
                headers=self.basic_headers,
            )

        result = response.json()
        self.assertEqual(result['data'][0]['os_id'], 'US2020052SV22HT')
        self.assertEqual(
            result['data'][0]['historical_os_id'], 'US20203545HUE4L'
        )

    def test_production_locations_aggregations(self):
        query = "?aggregation=geohex_grid&geohex_grid_precision=2"
        response = requests.get(
                f"{self.root_url}/api/v1/production-locations/{query}",
                headers=self.basic_headers,
            )

        result = response.json()
        self.assertIsNotNone(result['aggregations'])
        self.assertIsNotNone(result['aggregations']['geohex_grid'][0]['key'])
        self.assertIsNotNone(
            result['aggregations']['geohex_grid'][0]['doc_count']
        )

    def test_production_locations_geo_bounding_box(self):
        doc = {
            "sector": [
                "Apparel"
            ],
            "address": "Test Address 2",
            "name": "Test Name 2",
            "country": {
                "alpha_2": "US"
            },
            "os_id": "US2020052SV22KJ",
            "coordinates": {
                "lon": -102.378162,
                "lat": 40.1166236
            },
        }
        self.open_search_client.index(
            index=self.production_locations_index_name,
            body=doc,
            id=self.open_search_client.count()
        )
        self.open_search_client.indices.refresh(
            index=self.production_locations_index_name
        )

        query = (
            "?geo_bounding_box[top]=41&geo_bounding_box[left]="
            "-103&geo_bounding_box[bottom]=39&geo_bounding_box[right]=-101"
        )
        response = requests.get(
                f"{self.root_url}/api/v1/production-locations/{query}",
                headers=self.basic_headers,
            )

        result = response.json()
        self.assertIsNotNone(result['data'])
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['os_id'], 'US2020052SV22KJ')

    def test_production_locations_geo_polygon(self):
        inside_polygon = {
            "sector": ["Retail"],
            "address": "Inside Polygon Address",
            "name": "Inside Polygon Location",
            "country": {"alpha_2": "US"},
            "os_id": "US202309INSIDE",
            "coordinates": {
                "lon": -73.3121232,
                "lat": 40.7667421
            },
        }
        
        outside_polygon = {
            "sector": ["Retail"],
            "address": "Outside Polygon Address",
            "name": "Outside Polygon Location",
            "country": {"alpha_2": "US"},
            "os_id": "US202309OUTSIDE",
            "coordinates": {
                "lon": -75.000000,
                "lat": 42.000000
            },
        }

        self.open_search_client.index(
            index=self.production_locations_index_name,
            body=inside_polygon,
            id=self.open_search_client.count()
        )
        self.open_search_client.index(
            index=self.production_locations_index_name,
            body=outside_polygon,
            id=self.open_search_client.count()
        )
        
        self.open_search_client.indices.refresh(
            index=self.production_locations_index_name
        )

        query = "?geo_polygon=40.8193217,-73.0273466&geo_polygon=40.7667421,-73.3121232&geo_polygon=40.8459614,-73.5528312"
        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/{query}",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertIsNotNone(result['data'])
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['os_id'], "US202309INSIDE")
