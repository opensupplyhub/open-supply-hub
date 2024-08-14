from api.tests.v1.base_production_locations_test \
    import BaseProductionLocationsTest


class ProductionLocationsTest(BaseProductionLocationsTest):

    def test_production_locations_status(self):
        self.client.login(
            email=self.superuser_email, password=self.superuser_password
        )

        response = self.client.get(
                '/api/v1/production-locations/'
            )

        self.assertEqual(response.status_code, 200)

    def test_production_locations_exact(self):
        self.client.login(
            email=self.superuser_email,
            password=self.superuser_password
        )

        search_name = "Jiaxing%20Rising%20Garments%20Co.%20Ltd"
        query = "?size=1&name={}&sort_by=name&order_by=asc".\
            format(search_name)

        response = self.client.get(
                '/api/v1/production-locations/{}'.format(query)
            )

        result = response.json()
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['data'][0]['os_id'], 'CN2024225RQ8DJR')
