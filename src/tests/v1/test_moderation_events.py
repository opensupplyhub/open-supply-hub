import requests
from .base_moderation_events_test \
    import BaseModerationEventsTest


class ModerationEventsTest(BaseModerationEventsTest):

    def test_moderation_events_status(self):
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/",
            headers=self.basic_headers,
        )
        self.assertEqual(response.status_code, 200)


    def test_moderation_events_exact(self):
        # Index a document
        doc = {
            "uuid":"1f35a90f-70a0-4c3e-8e06-2ed8e1fc6806",
            "created_at":"2024-10-10T20:00:00Z",
            "updated_at":"2024-10-10T20:00:00Z",
            "status_change_date":"2024-10-10T21:00:00Z",
            "request_type":"CREATE",
            "os_id": "null",
            "contributor_id": 8,
            "raw_data":{
                "country":"Colombia",
                "name":"Bogotá Tech Hub",
                "address":"505 Tech Dr, Bogotá"
            },
            "cleaned_data":{
                "country":{
                "name":"Colombia",
                "alpha_2":"CO",
                "alpha_3":"COL",
                "numeric":"170"
                },
                "name":"Bogotá Tech Hub",
                "address":"505 Tech Dr, Bogotá"
            },
            "geocode_result":{
                "latitude":4.711,
                "longitude":-74.0721
            },
            "status":"APPROVED",
            "source":"API",
            "claim_id": "null"
        }

        self.open_search_client.index(
            index=self.index_name,
            body=doc,
            id=self.open_search_client.count()
        )
        self.open_search_client.indices.refresh(
            index=self.index_name
        )

        search_name = "Silver Composite Textile Mills Ltd."
        query = f"?size=1&name={search_name}"

        response = requests.get(
                f"{self.root_url}/api/v1/production-locations/{query}",
                headers=self.basic_headers,
            )

        result = response.json()
        self.assertEqual(result['data'][0]['os_id'], 'BD2020052SV22HT')

    '''
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
            index=self.index_name,
            body=doc,
            id=self.open_search_client.count()
        )
        self.open_search_client.indices.refresh(
            index=self.index_name
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
    '''
