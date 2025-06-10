from opensearchpy import OpenSearch
from .opensearch_test_case import OpenSearchIntegrationTestCase


class OpenSearchTest(OpenSearchIntegrationTestCase):

    def setUp(self):
        super().setUp()
        self.client: OpenSearch = self.getClient()

    def test_connection(self):
        health = self.client.cluster.health()
        self.assertIn(health['status'], ['green', 'yellow'])

    def test_create_and_index_document(self):
        doc = {'title': 'Test Document'}
        response = self.client.index(
            index=self.production_locations_index_name,
            body=doc,
            id=self.client.count(),
            refresh=True
        )
        self.assertEqual(response['result'], 'created')

    def test_search_document(self):
        doc = {
            "sector": [
                "Apparel"
            ],
            "address": "NO.11 DONGQIAN LAKE AREA,YINXIAN AVENUE,NINGBO,CHINA",
            "name": "NINGBO HUAYI GARMENTS CO LTD",
            "country": {
                "alpha_2": "CN"
            },
            "os_id": "CN2024221G4W0WA",
            "coordinates": {
                "lon": 121.5504069,
                "lat": 29.8194363
            },
            "claim_status": "unclaimed"
        }
        self.client.index(
            index=self.production_locations_index_name,
            body=doc,
            id=self.client.count(),
            refresh=True
        )
        self.client.indices.refresh(index=self.production_locations_index_name)

        query = {
            'query': {
                'match': {
                    'name': 'HUAYI'
                }
            }
        }
        response = self.client.search(
            index=self.production_locations_index_name,
            body=query
        )
        self.assertGreater(response['hits']['total']['value'], 0)

    def test_search_document_with_long_address(self):
        doc = {
            "sector": [
                "Apparel"
            ],
            "address": "Land plot number 115, map sheet number 03, Cadastral map of Son Ha commune, Son Ha commune, Nho Quan district, Ninh Binh province, Vietnam",
            "name": "HAI VINH VN CO., LTD - NINH BINH BRANCH",
            "country": {
                "alpha_2": "VN"
            },
            "os_id": "VN2025093077Q64",
            "coordinates": {
                "lon": 105.8701316,
                "lat": 29.202120893
            },
        }
        self.client.index(
            index=self.production_locations_index_name,
            body=doc,
            id=self.client.count(),
            refresh=True
        )
        self.client.indices.refresh(index=self.production_locations_index_name)

        query = {
            'query': {
                'match_phrase': {
                    'address': {
                        'query': (
                            'Land plot number 115, map sheet number 03'
                            ', Cadastral map of '
                            'Son Ha commune, Son Ha commune, Nho Quan district, '
                            'Ninh Binh province, Vietnam'
                        ),
                        'slop': 4
                    }
                }
            }
        }
        response = self.client.search(
            index=self.production_locations_index_name,
            body=query
        )
        print(response)
        self.assertGreater(response['hits']['total']['value'], 0)

    def test_search_document_with_long_query(self):
            doc = {
                "sector": [
                    "Apparel"
                ],
                "address": "Mount Isa Mines Limited Copper Refineries",
                "name": "Copper Refineries Pty Ltd Mount Isa Mines Limited CRL",
                "country": {
                    "alpha_2": "AU"
                },
                "os_id": "AU2025093077Q64",
                "coordinates": {
                    "lat": -16.940004,
                    "lon": 145.7628965
                },
                "description": "Mount Isa Mines Limited Copper Refineries Pty Ltd CRL",
                "local_name": "Mount Isa Mines Limited Copper Refineries Pty Ltd CRL"
            }
            self.client.index(
                index=self.production_locations_index_name,
                body=doc,
                id=self.client.count(),
                refresh=True
            )
            self.client.indices.refresh(index=self.production_locations_index_name)

            query_text = "Mount Isa Mines Limited Copper Refineries Pty Ltd CRL"
            query = {
                'query': {
                    'bool': {
                        'must': [
                            {
                                'multi_match': {
                                    'query': query_text,
                                    'fields': ['name^3', 'address^2', 'description^2', 'local_name^2'],
                                    'type': 'phrase',
                                    'slop': 2
                                }
                            }
                        ],
                        'filter': [
                            {'term': {'country.alpha_2': 'AU'}}
                        ]
                    }
                }
            }
            response = self.client.search(
                index=self.production_locations_index_name,
                body=query
            )
            print(response)
            self.assertEqual(response['hits']['total']['value'], 1)
