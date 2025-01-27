import requests
from .base_api_test \
    import BaseAPITest


class ModerationEventsTest(BaseAPITest):

    def test_moderation_events_exact(self):
        moderation_id_wrong = '0f35a90f-70a0-4c3e-8e06-2ed8e1fc6800'
        response = requests.get(
                f"{self.root_url}/api/v1/moderation-events/{moderation_id_wrong}",
                headers=self.basic_headers,
            )

        self.assertEqual(response.status_code, 404)

        moderation_id = '1f35a90f-70a0-4c3e-8e06-2ed8e1fc6800'
        response = requests.get(
                f"{self.root_url}/api/v1/moderation-events/{moderation_id}",
                headers=self.basic_headers,
            )

        result = response.json()
        self.assertEqual(result['moderation_id'], moderation_id)

    def test_moderation_events_status(self):
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/",
            headers=self.basic_headers,
        )
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', result)
        self.assertIsInstance(result['data'], list)

    def test_filter_by_status(self):
        status = "APPROVED"
        query = f"?status={status}"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertTrue(all(event['status'] == status for event in result['data']))
        self.assertEqual(response.status_code, 200)

    def test_filter_by_request_type(self):
        request_type = "CREATE"
        query = f"?request_type={request_type}"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertTrue(all(event['request_type'] == request_type for event in result['data']))
        self.assertEqual(response.status_code, 200)

    def test_filter_by_source(self):
        source = "API"
        query = f"?source={source}"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertTrue(all(event['source'] == source for event in result['data']))
        self.assertEqual(response.status_code, 200)

    def test_combined_filters(self):
        status = "PENDING"
        request_type = "CLAIM"
        query = f"?status={status}&request_type={request_type}"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )

        result = response.json()
        self.assertTrue(all(event['status'] == status and event['request_type'] == request_type for event in result['data']))
        self.assertEqual(response.status_code, 200)

    def test_sort_by_created_at_ascending(self):
        query = "?sort_by=created_at&order_by=asc"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )
        result = response.json()
        dates = [event['created_at'] for event in result['data']]
        self.assertEqual(dates, sorted(dates))
        self.assertEqual(response.status_code, 200)

    def test_sort_by_created_at_descending(self):
        query = "?sort_by=created_at&order_by=desc"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )
        result = response.json()
        dates = [event['created_at'] for event in result['data']]
        self.assertEqual(dates, sorted(dates, reverse=True))
        self.assertEqual(response.status_code, 200)

    def test_sort_by_status_ascending(self):
        query = "?sort_by=status&order_by=asc"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )
        result = response.json()
        statuses = [event['status'] for event in result['data']]
        self.assertEqual(statuses, sorted(statuses))
        self.assertEqual(response.status_code, 200)

    def test_sort_by_status_descending(self):
        query = "?sort_by=status&order_by=desc"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )
        result = response.json()
        statuses = [event['status'] for event in result['data']]
        self.assertEqual(statuses, sorted(statuses, reverse=True))
        self.assertEqual(response.status_code, 200)

    def test_size_limit(self):
        size = 5
        query = f"?size={size}"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )
        result = response.json()
        self.assertLessEqual(len(result['data']), size)
        self.assertEqual(response.status_code, 200)

    def test_size_exceeds_max_limit(self):
        max_size = 10000
        query = f"?size={max_size + 1}"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertEqual(result['detail'], 'The request query is invalid.')

    def test_search_after_pagination(self):
        # Step 1: Get the first set of results
        initial_size = 3
        query = f"?size={initial_size}&sort_by=created_at&order_by=asc"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result['data']), initial_size)

        # Step 2: Use the last item in the initial response for search_after
        last_event = result['data'][-1]
        search_after_value = last_event['created_at']
        search_after_id = last_event['moderation_id']
        search_after_query = (
            f"?size={initial_size}&sort_by=created_at&order_by=asc"
            f"&search_after[value]={search_after_value}&search_after[id]={search_after_id}"
        )

        # Step 3: Fetch the next page using search_after
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{search_after_query}",
            headers=self.basic_headers,
        )
        next_page_result = response.json()
        self.assertEqual(response.status_code, 200)

        # Check that the first item of the next page is indeed after the last item of the previous page
        self.assertTrue(
            all(
                (event['created_at'] > search_after_value or
                (event['created_at'] == search_after_value and event['moderation_id'] > search_after_id))
                for event in next_page_result['data']
            )
        )

    def test_late_search_after(self):
        invalid_search_after_value = 999999999999999
        invalid_search_after_id = "invalid-id"
        query = (
            f"?sort_by=created_at&order_by=asc"
            f"&search_after[value]={invalid_search_after_value}&search_after[id]={invalid_search_after_id}"
        )

        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )
        result = response.json()
        self.assertEqual(result['data'], [])

    def test_date_gte_greater_than_date_lt(self):
        wrong_date_gte = '2024-11-01'
        wrong_date_lt = '2024-10-18'

        query = f"?date_gte={wrong_date_gte}&date_lt={wrong_date_lt}"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )
        result = response.json()

        self.assertEqual(response.status_code, 400)

        error = result['errors'][0]
        self.assertEqual(error['field'], 'date_gte')
        self.assertEqual(
            error['detail'],
            "The 'date_gte' must be less than or equal to 'date_lt'."
        )

    def test_valid_country(self):
        valid_country = 'US'
        query = f"?country={valid_country}"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )

        self.assertEqual(response.status_code, 200)

    def test_invalid_country(self):
        invalid_country = 'USA'
        query = f"?country={invalid_country}"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', result)
        self.assertEqual(len(result['errors']), 1)

        error = result['errors'][0]
        self.assertEqual(error['field'], 'country')
        self.assertEqual(error['detail'], "'usa' is not a valid alpha-2 country code.")

    def test_valid_moderation_id(self):
        valid_moderation_id = '3b50d60f-85b2-4a17-9f8d-5d3e1fc68198'
        query = f"?moderation_id={valid_moderation_id}"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )

        self.assertEqual(response.status_code, 200)

    def test_invalid_moderation_id(self):
        invalid_moderation_id = '123!'
        query = f"?moderation_id={invalid_moderation_id}"
        response = requests.get(
            f"{self.root_url}/api/v1/moderation-events/{query}",
            headers=self.basic_headers,
        )
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', result)
        self.assertEqual(len(result['errors']), 1)

        error = result['errors'][0]
        self.assertEqual(error['field'], 'moderation_dd')
        self.assertEqual(error['detail'], "Invalid uuid(s): 123!.")
