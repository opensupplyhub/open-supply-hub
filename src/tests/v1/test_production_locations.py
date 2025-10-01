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
        query = f"?size=3&name={search_name}"

        response = requests.get(
                f"{self.root_url}/api/v1/production-locations/{query}",
                headers=self.basic_headers,
            )

        result = response.json()
        filtered = [item for item in result['data'] if item['os_id'] == 'BD2020052SV22HT']
        self.assertTrue(filtered)

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
        filtered = [item for item in result['data'] if item['os_id'] == 'US2020052SV22KJ']
        self.assertTrue(filtered)

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
        self.assertEqual(result['data'][0]['os_id'], "GL202309INSIDE")

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

    def test_production_locations_claim_status_filtering(self):
        claimed_doc = {
            "sector": ["Apparel"],
            "address": "Claimed Facility Address",
            "name": "Claimed Facility",
            "country": {"alpha_2": "US"},
            "os_id": "US2023CLAIMED01",
            "coordinates": {"lon": -74.0060, "lat": 40.7128},
            "claim_status": "claimed",
            "claimed_at": "2023-06-15T10:30:00Z"
        }
        
        unclaimed_doc = {
            "sector": ["Apparel"],
            "address": "Unclaimed Facility Address",
            "name": "Unclaimed Facility",
            "country": {"alpha_2": "CA"},
            "os_id": "CA2023UNCLAIMED01",
            "coordinates": {"lon": -79.3832, "lat": 43.6532},
            "claim_status": "unclaimed"
        }
        
        pending_doc = {
            "sector": ["Apparel"],
            "address": "Pending Facility Address",
            "name": "Pending Facility",
            "country": {"alpha_2": "MX"},
            "os_id": "MX2023PENDING01",
            "coordinates": {"lon": -99.1332, "lat": 19.4326},
            "claim_status": "pending",
            "claimed_at": "2023-08-20T14:45:00Z"
        }

        for doc in [claimed_doc, unclaimed_doc, pending_doc]:
            self.open_search_client.index(
                index=self.production_locations_index_name,
                body=doc,
                id=self.open_search_client.count()
            )

        self.open_search_client.indices.refresh(
            index=self.production_locations_index_name
        )

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?claim_status=claimed",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(item['claim_status'] == 'claimed' for item in result['data']))

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?claim_status=claimed&claim_status=pending",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(item['claim_status'] in ['claimed', 'pending'] for item in result['data']))

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?claim_status=unclaimed",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(item['claim_status'] == 'unclaimed' for item in result['data']))

    def test_production_locations_claim_status_date_filtering(self):
        early_claimed_doc = {
            "sector": ["Apparel"],
            "address": "Early Claimed Facility",
            "name": "Early Claimed Facility",
            "country": {"alpha_2": "US"},
            "os_id": "US2023EARLY01",
            "coordinates": {"lon": -74.0060, "lat": 40.7128},
            "claim_status": "claimed",
            "claimed_at": "2023-01-15T10:30:00Z"
        }
        
        late_claimed_doc = {
            "sector": ["Apparel"],
            "address": "Late Claimed Facility",
            "name": "Late Claimed Facility",
            "country": {"alpha_2": "CA"},
            "os_id": "CA2023LATE01",
            "coordinates": {"lon": -79.3832, "lat": 43.6532},
            "claim_status": "claimed",
            "claimed_at": "2023-12-15T14:45:00Z"
        }

        for doc in [early_claimed_doc, late_claimed_doc]:
            self.open_search_client.index(
                index=self.production_locations_index_name,
                body=doc,
                id=self.open_search_client.count()
            )
        self.open_search_client.indices.refresh(
            index=self.production_locations_index_name
        )

        test_os_ids = {'US2023EARLY01', 'CA2023LATE01'}

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?claimed_at_gt=2023-06-01T00:00:00.000000Z&size=100",
            headers=self.basic_headers,
        )
        result = response.json()

        self.assertEqual(response.status_code, 200)
        filtered = [item for item in result['data'] if item['os_id'] in test_os_ids]
        self.assertTrue(all(item['claim_status'] == 'claimed' for item in filtered))

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?claimed_at_lt=2023-06-01T00:00:00.000000Z&size=100",
            headers=self.basic_headers,
        )
        result = response.json()

        self.assertEqual(response.status_code, 200)
        filtered = [item for item in result['data'] if item['os_id'] in test_os_ids]
        self.assertTrue(all(item['claim_status'] == 'claimed' for item in filtered))

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?claimed_at_gt=2023-01-01T00:00:00.000000Z&claimed_at_lt=2023-07-01T00:00:00.000000Z&size=100",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        filtered = [item for item in result['data'] if item['os_id'] in test_os_ids]
        self.assertTrue(all(item['claim_status'] == 'claimed' for item in filtered))

    def test_production_locations_claim_status_sorting(self):
        claimed_early_doc = {
            "sector": ["Apparel"],
            "address": "Early Claimed Facility",
            "name": "Early Claimed Facility",
            "country": {"alpha_2": "US"},
            "os_id": "US2023EARLY02",
            "coordinates": {"lon": -74.0060, "lat": 40.7128},
            "claim_status": "claimed",
            "claimed_at": "2023-01-15T10:30:00Z"
        }

        claimed_late_doc = {
            "sector": ["Apparel"],
            "address": "Late Claimed Facility",
            "name": "Late Claimed Facility",
            "country": {"alpha_2": "CA"},
            "os_id": "CA2023LATE02",
            "coordinates": {"lon": -79.3832, "lat": 43.6532},
            "claim_status": "claimed",
            "claimed_at": "2023-12-15T14:45:00Z"
        }

        unclaimed_doc = {
            "sector": ["Apparel"],
            "address": "Unclaimed Facility",
            "name": "Unclaimed Facility",
            "country": {"alpha_2": "MX"},
            "os_id": "MX2023UNCLAIMED02",
            "coordinates": {"lon": -99.1332, "lat": 19.4326},
            "claim_status": "unclaimed"
        }

        for doc in [claimed_early_doc, claimed_late_doc, unclaimed_doc]:
            self.open_search_client.index(
                index=self.production_locations_index_name,
                body=doc,
                id=self.open_search_client.count()
            )
        self.open_search_client.indices.refresh(
            index=self.production_locations_index_name
        )

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?sort_by=claim_status&order_by=asc&size=100",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['data'][0]['claim_status'], 'claimed')

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?sort_by=claim_status&order_by=desc&size=100",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['data'][0]['claim_status'], 'unclaimed')

    def test_production_locations_combined_claim_status_filters(self):
        claimed_us_doc = {
            "sector": ["Apparel"],
            "address": "US Claimed Facility",
            "name": "US Claimed Facility",
            "country": {"alpha_2": "US"},
            "os_id": "US2023COMBINED01",
            "coordinates": {"lon": -74.0060, "lat": 40.7128},
            "claim_status": "claimed",
            "claimed_at": "2023-06-15T10:30:00Z"
        }

        unclaimed_ca_doc = {
            "sector": ["Apparel"],
            "address": "CA Unclaimed Facility",
            "name": "CA Unclaimed Facility",
            "country": {"alpha_2": "CA"},
            "os_id": "CA2023COMBINED01",
            "coordinates": {"lon": -79.3832, "lat": 43.6532},
            "claim_status": "unclaimed"
        }

        pending_mx_doc = {
            "sector": ["Apparel"],
            "address": "MX Pending Facility",
            "name": "MX Pending Facility",
            "country": {"alpha_2": "MX"},
            "os_id": "MX2023COMBINED01",
            "coordinates": {"lon": -99.1332, "lat": 19.4326},
            "claim_status": "pending",
            "claimed_at": "2023-08-20T14:45:00Z"
        }

        for doc in [claimed_us_doc, unclaimed_ca_doc, pending_mx_doc]:
            self.open_search_client.index(
                index=self.production_locations_index_name,
                body=doc,
                id=self.open_search_client.count()
            )
        self.open_search_client.indices.refresh(
            index=self.production_locations_index_name
        )

        test_os_ids = {'US2023COMBINED01', 'CA2023COMBINED01', 'MX2023COMBINED01'}

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?claim_status=claimed&country=US&size=100",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        filtered = [item for item in result['data'] if item['os_id'] in test_os_ids]
        self.assertTrue(all(item['claim_status'] == 'claimed' for item in filtered))
        self.assertTrue(all(item['country']['alpha_2'] == 'US' for item in filtered))

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?claim_status=claimed&claimed_at_gt=2023-05-01T00:00:00.000000Z&size=100",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        filtered = [item for item in result['data'] if item['os_id'] in test_os_ids]
        self.assertTrue(all(item['claim_status'] == 'claimed' for item in filtered))

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?claim_status=claimed&claim_status=pending&country=US&country=MX&size=100",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        filtered = [item for item in result['data'] if item['os_id'] in test_os_ids]
        os_ids = [item['os_id'] for item in filtered]
        self.assertIn('MX2023COMBINED01', os_ids)
        self.assertTrue(all(item['claim_status'] in ['claimed', 'pending'] for item in filtered))
        self.assertTrue(all(item['country']['alpha_2'] in ['US', 'MX'] for item in filtered))

    def test_production_locations_claim_status_invalid_filters(self):
        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?claim_status=invalid_status",
            headers=self.basic_headers,
        )

        if response.status_code == 400:
            result = response.json()
            self.assertEqual(result['detail'], 'The request query is invalid.')
            self.assertEqual(result['errors'][0]['field'], 'claim_status')

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?claimed_at_gt=invalid-date",
            headers=self.basic_headers,
        )

        if response.status_code == 400:
            result = response.json()
            self.assertEqual(result['detail'], 'The request query is invalid.')

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?sort_by=invalid_field",
            headers=self.basic_headers,
        )

        if response.status_code == 400:
            result = response.json()
            self.assertEqual(result['detail'], 'The request query is invalid.')
            self.assertEqual(result['errors'][0]['field'], 'sort_by')

    def test_production_locations_claimed_at_sort_asc(self):
        test_docs = [
            {
                "sector": ["Electronics"],
                "address": "Test Sort ASC Address A",
                "name": "Facility TR ASC A",
                "country": {"alpha_2": "TR"},
                "os_id": "US2023SORT01",
                "coordinates": {"lon": -73.0060, "lat": 40.7128},
                "claim_status": "claimed",
                "claimed_at": "2022-06-15T10:30:00Z"
            },
            {
                "sector": ["Electronics"],
                "address": "Test Sort ASC Address B",
                "name": "Facility TR ASC B",
                "country": {"alpha_2": "TR"},
                "os_id": "US2023SORT02",
                "coordinates": {"lon": -72.0060, "lat": 40.7128},
                "claim_status": "claimed",
                "claimed_at": "2022-07-01T09:00:00Z"
            },
            {
                "sector": ["Electronics"],
                "address": "Test Sort ASC Address C",
                "name": "Facility TR ASC C",
                "country": {"alpha_2": "TR"},
                "os_id": "US2023SORT03",
                "coordinates": {"lon": -71.0060, "lat": 40.7128},
                "claim_status": "claimed",
                "claimed_at": "2022-05-01T15:45:00Z"
            }
        ]

        for i, doc in enumerate(test_docs):
            self.open_search_client.index(
                index=self.production_locations_index_name,
                body=doc,
                id=f"test_sort_doc_{i}"
            )

        self.open_search_client.indices.refresh(index=self.production_locations_index_name)

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?sort_by=claimed_at&order_by=asc&size=10",
            headers=self.basic_headers,
        )

        result = response.json()
        claimed_results = [item for item in result['data'] if item.get('claimed_at')]

        self.assertGreaterEqual(len(claimed_results), 2, "Need at least 2 results with claimed_at for comparison")

        claimed_ats = [item['claimed_at'] for item in claimed_results]
        sorted_claimed_ats = sorted(claimed_ats)
        self.assertEqual(claimed_ats[:len(sorted_claimed_ats)], sorted_claimed_ats)

    def test_production_locations_claimed_at_sort_desc(self):
        test_docs = [
            {
                "sector": ["Apparel"],
                "address": "Test Sort DESC Address A",
                "name": "Facility US DESC A",
                "country": {"alpha_2": "US"},
                "os_id": "US2023SORT01",
                "coordinates": {"lon": -74.0060, "lat": 40.7128},
                "claim_status": "claimed",
                "claimed_at": "2023-06-15T10:30:00Z"
            },
            {
                "sector": ["Apparel"],
                "address": "Test Sort DESC Address B",
                "name": "Facility US DESC B",
                "country": {"alpha_2": "US"},
                "os_id": "US2023SORT02",
                "coordinates": {"lon": -74.0060, "lat": 40.7128},
                "claim_status": "claimed",
                "claimed_at": "2023-07-01T09:00:00Z"
            },
            {
                "sector": ["Apparel"],
                "address": "Test Sort DESC Address C",
                "name": "Facility US DESC C",
                "country": {"alpha_2": "US"},
                "os_id": "US2023SORT03",
                "coordinates": {"lon": -74.0060, "lat": 40.7128},
                "claim_status": "claimed",
                "claimed_at": "2023-05-01T15:45:00Z"
            }
        ]

        for i, doc in enumerate(test_docs):
            self.open_search_client.index(
                index=self.production_locations_index_name,
                body=doc,
                id=f"test_sort_desc_doc_{i}"
            )

        self.open_search_client.indices.refresh(index=self.production_locations_index_name)

        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/?sort_by=claimed_at&order_by=desc&size=10",
            headers=self.basic_headers,
        )

        result = response.json()
        claimed_results = [item for item in result['data'] if item.get('claimed_at')]

        self.assertGreaterEqual(len(claimed_results), 2, "Need at least 2 results with claimed_at for comparison")

        claimed_ats = [item['claimed_at'] for item in claimed_results]
        sorted_claimed_ats = sorted(claimed_ats, reverse=True)
        self.assertEqual(claimed_ats[:len(sorted_claimed_ats)], sorted_claimed_ats)

    def test_claim_date_gte_greater_than_claim_date_lt(self):
        wrong_date_gte = '2024-11-01T13:49:51.141Z'
        wrong_date_lt = '2024-10-18T13:49:51.141Z'

        query = f"?claimed_at_gt={wrong_date_gte}&claimed_at_lt={wrong_date_lt}"
        response = requests.get(
            f"{self.root_url}/api/v1/production-locations/{query}",
            headers=self.basic_headers,
        )
        result = response.json()

        self.assertEqual(response.status_code, 400)

        error = result['errors'][0]
        self.assertEqual(error['field'], 'claimed_at_gt')
        self.assertEqual(
            error['detail'],
            "The 'claimed_at_gt' must be less than or equal to 'claimed_at_lt'."
        )

    def test_production_locations_country(self):

        response = requests.get(
                f"{self.root_url}/api/v1/production-locations/",
                headers=self.basic_headers,
                timeout=30,
            )

        result = response.json()
        self.assertTrue(len(result['data']) > 0)
        first_location = result['data'][0]
        self.assertDictEqual(first_location, {'name': 'Location name'})