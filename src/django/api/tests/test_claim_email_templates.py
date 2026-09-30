"""
The claim-submitted confirmation email swaps its eligibility sentence
with the relaxed_claim_eligibility switch (employees may claim).
"""
from django.template.loader import get_template
from django.test import TestCase


class ClaimSubmittedEmailEligibilityTest(TestCase):
    CONTEXT = {
        'facility_name': 'Test Mill',
        'facility_address': '1 Test Street',
        'facility_url': 'https://example.com/facilities/X',
    }

    TEMPLATES = (
        'mail/claim_facility_submitted_body.txt',
        'mail/claim_facility_submitted_body.html',
        'mail/claim_facility_submitted_body_pause_version.txt',
        'mail/claim_facility_submitted_body_pause_version.html',
    )

    def render(self, template, relaxed):
        return get_template(template).render(
            {**self.CONTEXT, 'relaxed_eligibility': relaxed}
        )

    def test_default_keeps_owner_senior_management_wording(self):
        for template in self.TEMPLATES:
            body = self.render(template, relaxed=False)
            self.assertIn('owner or senior management', body, template)
            self.assertNotIn(
                'employee\n            of the production location', body,
                template,
            )

    def test_relaxed_switch_swaps_to_employee_wording(self):
        for template in self.TEMPLATES:
            body = self.render(template, relaxed=True)
            self.assertNotIn('owner or senior management', body, template)
            self.assertIn('employee', body, template)
            self.assertIn('parent', body, template)
