from django.test import TestCase
from api.models.facility.claims_reason import ClaimsReason


class ClaimsReasonTest(TestCase):
    def setUp(self):
        self.reason1 = ClaimsReason.objects.create(
            text="Acme Inc"
        )
        self.reason2 = ClaimsReason.objects.create(
            text="Global Fashion Corp"
        )
        self.inactive_reason = ClaimsReason.objects.create(
            text="Inactive Brand Ltd",
            is_active=False
        )

    def test_claims_reason_creation(self):
        self.assertEqual(self.reason1.text, "Acme Inc")
        self.assertTrue(self.reason1.is_active)
        self.assertIsNotNone(self.reason1.created_at)
        self.assertIsNotNone(self.reason1.updated_at)

    def test_claims_reason_string_representation(self):
        self.assertEqual(str(self.reason1), "Acme Inc")

    def test_claims_reason_ordering(self):
        reasons = ClaimsReason.objects.all()
        self.assertEqual(reasons[0].text, "Acme Inc")  # Alphabetical first
        self.assertEqual(reasons[1].text, "Global Fashion Corp")

    def test_active_claims_reasons_only(self):
        active_reasons = ClaimsReason.objects.filter(is_active=True)
        self.assertEqual(active_reasons.count(), 2)
        self.assertNotIn(self.inactive_reason, active_reasons)

    def test_text_max_length(self):
        long_text = "x" * 101
        reason = ClaimsReason(text=long_text)
        with self.assertRaises(Exception):
            reason.full_clean()

    def test_text_uniqueness(self):
        with self.assertRaises(Exception):
            ClaimsReason.objects.create(text="Acme Inc")