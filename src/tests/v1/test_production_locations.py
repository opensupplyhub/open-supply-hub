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
        doc = {
            "sector": ["Apparel"],
            "address": "Test Address",
            "name": "Test Facility",
            "country": {
                "name": "United States",
                "alpha_2": "US",
                "alpha_3": "USA",
                "numeric": "840"
            },
            "os_id": "US2020052SV22HT",
            "coordinates": {
                "lon": -75.000000,
                "lat": 40.000000
            }
        }
        self.open_search_client.index(
            index=self.production_locations_index_name,
            body=doc,
            id=self.open_search_client.count(),
            refresh=True
        )

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

    def test_production_locations_geo_polygon_outside(self):
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
            body=outside_polygon,
            id=self.open_search_client.count()
        )

        self.open_search_client.indices.refresh(
            index=self.production_locations_index_name
        )

        query = "?geo_polygon=79.318492,-39.36719&geo_polygon=79.280399,-55.39907&geo_polygon=77.57295,-55.512304&geo_polygon=77.598154,-38.396004"
        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/{query}",
            headers=self.basic_headers,
        )

        result = response.json()
        os_ids = {item["os_id"] for item in result["data"]}
        self.assertNotIn("US202309OUTSIDE", os_ids)

    def test_production_locations_geo_polygon_inside(self):
        inside_polygon = {
            "sector": ["Retail"],
            "address": "Inside Polygon Address",
            "name": "Inside Polygon Location",
            "country": {"alpha_2": "GL"},
            "os_id": "GL202309INSIDE",
            "coordinates": {
                "lon": -47.0,
                "lat": 78.0
            },
        }

        self.open_search_client.index(
            index=self.production_locations_index_name,
            body=inside_polygon,
            id=self.open_search_client.count()
        )

        self.open_search_client.indices.refresh(
            index=self.production_locations_index_name
        )

        query = "?geo_polygon=79.318492,-39.36719&geo_polygon=79.280399,-55.39907&geo_polygon=77.57295,-55.512304&geo_polygon=77.598154,-38.396004"
        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/{query}",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertIsNotNone(result['data'])
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['os_id'], "GL202309INSIDE")

    def test_production_locations_with_more_than_hundred_points(self):
        doc = {
            "sector": ["Apparel"],
            "address": "Test Address",
            "name": "Test Facility",
            "country": {
                "alpha_2": "US"
            },
            "os_id": "US2020052SV22HT",
            "coordinates": {
                "lon": 0.0,
                "lat": 45.0
            }
        }
        self.open_search_client.index(
            index=self.production_locations_index_name,
            body=doc,
            id=self.open_search_client.count(),
            refresh=True
        )

        query = (
            "?geo_polygon=71.0,-25.0&geo_polygon=70.5,-22.0&geo_polygon=70.0,-19.0"
            "&geo_polygon=69.5,-16.0&geo_polygon=69.0,-13.0&geo_polygon=68.5,-10.0"
            "&geo_polygon=68.0,-7.0&geo_polygon=67.5,-4.0&geo_polygon=67.0,-1.0"
            "&geo_polygon=66.5,2.0&geo_polygon=66.0,5.0&geo_polygon=65.5,8.0"
            "&geo_polygon=65.0,11.0&geo_polygon=64.5,14.0&geo_polygon=64.0,17.0"
            "&geo_polygon=63.5,20.0&geo_polygon=63.0,23.0&geo_polygon=62.5,26.0"
            "&geo_polygon=62.0,29.0&geo_polygon=61.5,32.0&geo_polygon=61.0,35.0"
            "&geo_polygon=60.5,38.0&geo_polygon=60.0,41.0&geo_polygon=59.5,44.0"
            "&geo_polygon=59.0,47.0&geo_polygon=58.5,50.0&geo_polygon=58.0,53.0"
            "&geo_polygon=57.5,56.0&geo_polygon=57.0,59.0&geo_polygon=56.5,62.0"
            "&geo_polygon=56.0,65.0&geo_polygon=55.5,68.0&geo_polygon=55.0,71.0"
            "&geo_polygon=54.5,74.0&geo_polygon=54.0,77.0&geo_polygon=53.5,80.0"
            "&geo_polygon=53.0,83.0&geo_polygon=52.5,86.0&geo_polygon=52.0,89.0"
            "&geo_polygon=51.5,92.0&geo_polygon=51.0,95.0&geo_polygon=50.5,98.0"
            "&geo_polygon=50.0,101.0&geo_polygon=49.5,104.0&geo_polygon=49.0,107.0"
            "&geo_polygon=48.5,110.0&geo_polygon=48.0,113.0&geo_polygon=47.5,116.0"
            "&geo_polygon=47.0,119.0&geo_polygon=46.5,122.0&geo_polygon=46.0,125.0"
            "&geo_polygon=45.5,128.0&geo_polygon=45.0,131.0&geo_polygon=44.5,134.0"
            "&geo_polygon=44.0,137.0&geo_polygon=43.5,140.0&geo_polygon=43.0,143.0"
            "&geo_polygon=42.5,146.0&geo_polygon=42.0,149.0&geo_polygon=41.5,152.0"
            "&geo_polygon=41.0,155.0&geo_polygon=40.5,158.0&geo_polygon=40.0,161.0"
            "&geo_polygon=39.5,164.0&geo_polygon=39.0,167.0&geo_polygon=38.5,170.0"
            "&geo_polygon=38.0,173.0&geo_polygon=37.5,176.0&geo_polygon=37.0,179.0"
            "&geo_polygon=36.5,-178.0&geo_polygon=36.0,-175.0&geo_polygon=35.5,-172.0"
            "&geo_polygon=35.0,-169.0&geo_polygon=34.5,-166.0&geo_polygon=34.0,-163.0"
            "&geo_polygon=33.5,-160.0&geo_polygon=33.0,-157.0&geo_polygon=32.5,-154.0"
            "&geo_polygon=32.0,-151.0&geo_polygon=31.5,-148.0&geo_polygon=31.0,-145.0"
            "&geo_polygon=30.5,-142.0&geo_polygon=30.0,-139.0&geo_polygon=29.5,-136.0"
            "&geo_polygon=29.0,-133.0&geo_polygon=28.5,-130.0&geo_polygon=28.0,-127.0"
            "&geo_polygon=27.5,-124.0&geo_polygon=27.0,-121.0&geo_polygon=26.5,-118.0"
            "&geo_polygon=26.0,-115.0&geo_polygon=25.5,-112.0&geo_polygon=25.0,-109.0"
            "&geo_polygon=24.5,-106.0&geo_polygon=24.0,-103.0&geo_polygon=23.5,-100.0"
            "&geo_polygon=23.0,-97.0&geo_polygon=22.5,-94.0&geo_polygon=22.0,-91.0"
            "&geo_polygon=21.5,-88.0&geo_polygon=21.0,-85.0&geo_polygon=20.5,-82.0"
            "&geo_polygon=20.0,-79.0&geo_polygon=19.5,-76.0&geo_polygon=19.0,-73.0"
            "&geo_polygon=18.5,-70.0&geo_polygon=18.0,-67.0&geo_polygon=17.5,-64.0"
            "&geo_polygon=17.0,-61.0&geo_polygon=16.5,-58.0&geo_polygon=16.0,-55.0"
            "&geo_polygon=15.5,-52.0&geo_polygon=15.0,-49.0&geo_polygon=14.5,-46.0"
            "&geo_polygon=14.0,-43.0&geo_polygon=13.5,-40.0&geo_polygon=13.0,-37.0"
            "&geo_polygon=12.5,-34.0&geo_polygon=12.0,-31.0&geo_polygon=11.5,-28.0"
            "&geo_polygon=11.0,-25.0&geo_polygon=10.5,-22.0&geo_polygon=10.0,-19.0"
        )

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/{query}",
            headers=self.basic_headers,
        )

        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertIsNotNone(result['data'])
        self.assertGreater(len(result['data']), 0)

    def test_production_locations_with_missed_geo_polygon_value(self):
        query = (
            "?geo_polygon=79.318492,-39.36719&"
            "geo_polygon=79.280399,-55.39907&"
            "geo_polygon=&geo_polygon="
        )

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/{query}",
            headers=self.basic_headers,
        )

        self.assertEqual(response.status_code, 400)

        result = response.json()
        self.assertEqual(result['detail'], 'The request query is invalid.')
        self.assertEqual(result['errors'][0]['field'], 'geo_polygon')
        self.assertEqual(result['errors'][0]['detail'], 'This field may not be blank.')

    def test_production_locations_additional_identifiers(self):
        doc = {
            "sector": [
                "Apparel"
            ],
            "address": "Test Address",
            "name": "Test Name",
            "country": {
                "alpha_2": "US"
            },
            "os_id": "UC3020952SV27JF",
            "coordinates": {
                "lon": 90.378162,
                "lat": 24.1166236
            },
            "rba_id": "RBA-12345678",
            "duns_id": "150483782",
            "lei_id": "529900T8BM49AURSDO55"
        }
        expected_rba_id = "RBA-12345678"
        expected_duns_id = "150483782"
        expected_lei_id = "529900T8BM49AURSDO55"

        self.open_search_client.index(
            index=self.production_locations_index_name,
            body=doc,
            id=self.open_search_client.count()
        )
        self.open_search_client.indices.refresh(
            index=self.production_locations_index_name
        )

        search_os_id = "UC3020952SV27JF"
        query = f"?size=1&os_id={search_os_id}"

        response = requests.get(
                f"{self.root_url}/api/v1/production-locations/{query}",
                headers=self.basic_headers,
            )

        result = response.json()
        self.assertEqual(
            result['data'][0]['rba_id'],
            expected_rba_id
        )
        self.assertEqual(
            result['data'][0]['duns_id'],
            expected_duns_id
        )
        self.assertEqual(
            result['data'][0]['lei_id'],
            expected_lei_id
        )
