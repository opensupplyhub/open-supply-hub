import json
from django.test import TestCase
from django.urls import reverse
from api.models import User, Contributor


class CampaignCodeAPITest(TestCase):
    """Test campaign code API integration"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create(email="test@example.com")
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="Test Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE
        )
        
        # Create superuser for API access
        self.superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="testpass123"
        )

    def test_user_profile_includes_campaign_code(self):
        """Test that user profile includes campaign code for contributors"""
        self.client.login(email="admin@example.com", password="testpass123")
        response = self.client.get(f"/user-profile/{self.user.id}/")

        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        # Should include campaign code fields
        self.assertIn('campaign_code', data)
        self.assertIn('campaign_code_valid', data)

        # Campaign code should be properly formatted
        campaign_code = data['campaign_code']
        self.assertIsNotNone(campaign_code)
        self.assertTrue(campaign_code.startswith('CC'))
        self.assertEqual(len(campaign_code), 7)

        # Campaign code should be valid
        self.assertTrue(data['campaign_code_valid'])

    def test_user_profile_without_contributor_campaign_code(self):
        """Test that users without contributors get null campaign code"""
        # Create a user without a contributor
        user_without_contributor = User.objects.create(
            email="nocontributor@example.com"
        )
        
        self.client.login(email="admin@example.com", password="testpass123")
        response = self.client.get(f"/user-profile/{user_without_contributor.id}/")

        self.assertEqual(200, response.status_code)

        data = json.loads(response.content)

        # Campaign code should be null for users without contributors
        self.assertIsNone(data['campaign_code'])
        self.assertFalse(data['campaign_code_valid'])

    def test_validate_campaign_code_endpoint_valid_code(self):
        """Test campaign code validation endpoint with valid code"""
        # Get the campaign code for our test contributor
        campaign_code = self.contributor.campaign_code
        
        response = self.client.get(f"/api/validate-campaign-code/{campaign_code}/")
        
        self.assertEqual(200, response.status_code)
        
        data = json.loads(response.content)
        
        self.assertEqual(data['code'], campaign_code)
        self.assertTrue(data['valid'])
        self.assertEqual(data['contributor_id'], self.contributor.id)

    def test_validate_campaign_code_endpoint_invalid_code(self):
        """Test campaign code validation endpoint with invalid code"""
        invalid_code = "CC00016"  # This should be invalid
        
        response = self.client.get(f"/api/validate-campaign-code/{invalid_code}/")
        
        self.assertEqual(200, response.status_code)
        
        data = json.loads(response.content)
        
        self.assertEqual(data['code'], invalid_code)
        self.assertFalse(data['valid'])
        self.assertIsNone(data['contributor_id'])

    def test_validate_campaign_code_endpoint_malformed_code(self):
        """Test campaign code validation endpoint with malformed code"""
        malformed_code = "INVALID"
        
        response = self.client.get(f"/api/validate-campaign-code/{malformed_code}/")
        
        self.assertEqual(200, response.status_code)
        
        data = json.loads(response.content)
        
        self.assertEqual(data['code'], malformed_code)
        self.assertFalse(data['valid'])
        self.assertIsNone(data['contributor_id'])

    def test_validate_campaign_code_endpoint_empty_code(self):
        """Test campaign code validation endpoint with empty code"""
        response = self.client.get("/api/validate-campaign-code//")
        
        # This should result in a 404 or similar due to URL routing
        # Or we could handle it as a 400 if the view catches it
        self.assertIn(response.status_code, [400, 404])

    def test_campaign_code_consistency(self):
        """Test that campaign codes are consistent across API calls"""
        self.client.login(email="admin@example.com", password="testpass123")
        
        # Get campaign code from profile endpoint
        profile_response = self.client.get(f"/user-profile/{self.user.id}/")
        profile_data = json.loads(profile_response.content)
        profile_campaign_code = profile_data['campaign_code']
        
        # Get the same code directly from the model
        model_campaign_code = self.contributor.campaign_code
        
        # They should be identical
        self.assertEqual(profile_campaign_code, model_campaign_code)
        
        # Validate both through the validation endpoint
        validation_response = self.client.get(f"/api/validate-campaign-code/{profile_campaign_code}/")
        validation_data = json.loads(validation_response.content)
        
        self.assertTrue(validation_data['valid'])
        self.assertEqual(validation_data['contributor_id'], self.contributor.id)

    def test_multiple_contributors_unique_codes(self):
        """Test that different contributors get different campaign codes via API"""
        # Create another contributor
        user2 = User.objects.create(email="test2@example.com")
        contributor2 = Contributor.objects.create(
            admin=user2,
            name="Test Contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE
        )
        
        self.client.login(email="admin@example.com", password="testpass123")
        
        # Get both campaign codes via API
        response1 = self.client.get(f"/user-profile/{self.user.id}/")
        response2 = self.client.get(f"/user-profile/{user2.id}/")
        
        data1 = json.loads(response1.content)
        data2 = json.loads(response2.content)
        
        code1 = data1['campaign_code']
        code2 = data2['campaign_code']
        
        # Codes should be different
        self.assertNotEqual(code1, code2)
        
        # Both should be valid
        self.assertTrue(data1['campaign_code_valid'])
        self.assertTrue(data2['campaign_code_valid'])
        
        # Validate both codes map to correct contributors
        validation1 = self.client.get(f"/api/validate-campaign-code/{code1}/")
        validation2 = self.client.get(f"/api/validate-campaign-code/{code2}/")
        
        val_data1 = json.loads(validation1.content)
        val_data2 = json.loads(validation2.content)
        
        self.assertEqual(val_data1['contributor_id'], self.contributor.id)
        self.assertEqual(val_data2['contributor_id'], contributor2.id)