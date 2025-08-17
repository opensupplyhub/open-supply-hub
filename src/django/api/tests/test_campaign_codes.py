from django.test import TestCase
from api.models import Contributor, User
from api.helpers.helpers import (
    calculate_luhn_check_digit,
    generate_contributor_campaign_code,
    validate_contributor_campaign_code,
    extract_contributor_id_from_campaign_code
)


class CampaignCodeHelpersTest(TestCase):
    """Test campaign code helper functions"""

    def test_luhn_check_digit_calculation(self):
        """Test Luhn algorithm check digit calculation"""
        # Test known values
        self.assertEqual(calculate_luhn_check_digit("990001"), 1)
        self.assertEqual(calculate_luhn_check_digit("990015"), 5)
        self.assertEqual(calculate_luhn_check_digit("990156"), 4)
        self.assertEqual(calculate_luhn_check_digit("990999"), 5)

    def test_luhn_check_digit_invalid_input(self):
        """Test Luhn algorithm with invalid input"""
        with self.assertRaises(ValueError):
            calculate_luhn_check_digit("abc123")
        with self.assertRaises(ValueError):
            calculate_luhn_check_digit("123.45")
        with self.assertRaises(ValueError):
            calculate_luhn_check_digit("")

    def test_generate_contributor_campaign_code(self):
        """Test campaign code generation"""
        # Test specific known values
        self.assertEqual(generate_contributor_campaign_code(1), "CC00011")
        self.assertEqual(generate_contributor_campaign_code(15), "CC00155")
        self.assertEqual(generate_contributor_campaign_code(156), "CC01564")
        self.assertEqual(generate_contributor_campaign_code(999), "CC09995")

    def test_generate_campaign_code_format(self):
        """Test campaign code format consistency"""
        # Test various IDs
        test_ids = [1, 42, 100, 500, 1000, 9999]
        for test_id in test_ids:
            code = generate_contributor_campaign_code(test_id)
            # Should always be 7 characters
            self.assertEqual(len(code), 7)
            # Should start with CC
            self.assertTrue(code.startswith("CC"))
            # Should be all digits after CC
            self.assertTrue(code[2:].isdigit())

    def test_generate_campaign_code_invalid_input(self):
        """Test campaign code generation with invalid input"""
        with self.assertRaises(ValueError):
            generate_contributor_campaign_code(0)
        with self.assertRaises(ValueError):
            generate_contributor_campaign_code(-1)
        with self.assertRaises(ValueError):
            generate_contributor_campaign_code("123")
        with self.assertRaises(ValueError):
            generate_contributor_campaign_code(1.5)

    def test_validate_contributor_campaign_code(self):
        """Test campaign code validation"""
        # Valid codes
        self.assertTrue(validate_contributor_campaign_code("CC00011"))
        self.assertTrue(validate_contributor_campaign_code("CC00155"))
        self.assertTrue(validate_contributor_campaign_code("CC01564"))
        self.assertTrue(validate_contributor_campaign_code("CC09995"))

        # Invalid codes - wrong check digits
        self.assertFalse(validate_contributor_campaign_code("CC00016"))
        self.assertFalse(validate_contributor_campaign_code("CC00158"))
        self.assertFalse(validate_contributor_campaign_code("CC01563"))

        # Invalid codes - wrong format
        self.assertFalse(validate_contributor_campaign_code("XX00016"))
        self.assertFalse(validate_contributor_campaign_code("CC0001"))
        self.assertFalse(validate_contributor_campaign_code("CC000166"))
        self.assertFalse(validate_contributor_campaign_code("CC00ABC"))
        self.assertFalse(validate_contributor_campaign_code(""))
        self.assertFalse(validate_contributor_campaign_code(None))
        self.assertFalse(validate_contributor_campaign_code(123))

    def test_extract_contributor_id_from_campaign_code(self):
        """Test extracting contributor ID from campaign codes"""
        # Valid extractions
        self.assertEqual(extract_contributor_id_from_campaign_code("CC00011"), 1)
        self.assertEqual(extract_contributor_id_from_campaign_code("CC00155"), 15)
        self.assertEqual(extract_contributor_id_from_campaign_code("CC01564"), 156)
        self.assertEqual(extract_contributor_id_from_campaign_code("CC09995"), 999)

        # Invalid codes should return None
        self.assertIsNone(extract_contributor_id_from_campaign_code("CC00016"))
        self.assertIsNone(extract_contributor_id_from_campaign_code("XX00016"))
        self.assertIsNone(extract_contributor_id_from_campaign_code("CC0001"))
        self.assertIsNone(extract_contributor_id_from_campaign_code(""))
        self.assertIsNone(extract_contributor_id_from_campaign_code(None))

    def test_luhn_error_detection(self):
        """Test that Luhn algorithm catches common errors"""
        base_code = "CC00011"  # Valid code for contributor ID 1
        
        # Single digit errors
        invalid_codes = [
            "CC10011",  # First digit changed
            "CC01011",  # Second digit changed
            "CC00111",  # Third digit changed
            "CC00021",  # Fourth digit changed
            "CC00010",  # Check digit changed
        ]
        
        for invalid_code in invalid_codes:
            self.assertFalse(
                validate_contributor_campaign_code(invalid_code),
                f"Code {invalid_code} should be invalid"
            )

        # Additional validation - Luhn algorithm catches most common errors
        # We've already tested single digit changes above


class ContributorCampaignCodeTest(TestCase):
    """Test campaign code functionality on Contributor model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create(email="test@example.com")
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name="Test Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE
        )

    def test_contributor_campaign_code_property(self):
        """Test that contributor campaign_code property works"""
        # Get the campaign code
        code = self.contributor.campaign_code
        
        # Should be a valid code
        self.assertTrue(validate_contributor_campaign_code(code))
        
        # Should be consistent (same code each time)
        self.assertEqual(code, self.contributor.campaign_code)
        
        # Should extract back to the same contributor ID
        extracted_id = extract_contributor_id_from_campaign_code(code)
        self.assertEqual(extracted_id, self.contributor.id)

    def test_multiple_contributors_unique_codes(self):
        """Test that different contributors get different codes"""
        # Create additional contributors
        user2 = User.objects.create(email="test2@example.com")
        contributor2 = Contributor.objects.create(
            admin=user2,
            name="Test Contributor 2",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE
        )
        
        user3 = User.objects.create(email="test3@example.com")
        contributor3 = Contributor.objects.create(
            admin=user3,
            name="Test Contributor 3",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE
        )
        
        # All codes should be different
        code1 = self.contributor.campaign_code
        code2 = contributor2.campaign_code
        code3 = contributor3.campaign_code
        
        self.assertNotEqual(code1, code2)
        self.assertNotEqual(code1, code3)
        self.assertNotEqual(code2, code3)
        
        # All codes should be valid
        self.assertTrue(validate_contributor_campaign_code(code1))
        self.assertTrue(validate_contributor_campaign_code(code2))
        self.assertTrue(validate_contributor_campaign_code(code3))

    def test_campaign_code_deterministic(self):
        """Test that campaign codes are deterministic"""
        # Same contributor should always get the same code
        code1 = self.contributor.campaign_code
        code2 = self.contributor.campaign_code
        
        self.assertEqual(code1, code2)
        
        # Even after refresh from database
        self.contributor.refresh_from_db()
        code3 = self.contributor.campaign_code
        
        self.assertEqual(code1, code3)

    def test_campaign_code_format_compliance(self):
        """Test that generated codes comply with expected format"""
        code = self.contributor.campaign_code
        
        # Should be exactly 7 characters
        self.assertEqual(len(code), 7)
        
        # Should start with CC
        self.assertTrue(code.startswith("CC"))
        
        # Should be uppercase
        self.assertEqual(code, code.upper())
        
        # Should contain only alphanumeric characters (in this case, only digits after CC)
        self.assertTrue(code[2:].isdigit())