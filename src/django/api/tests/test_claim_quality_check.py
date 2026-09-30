import json
from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.db.models.signals import post_save
from django.test import override_settings
from rest_framework.test import APITestCase
from waffle.testutils import override_switch

from api.constants import FacilityClaimStatuses
from api.models import (
    Contributor,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    ModerationEvent,
    Sector,
    Source,
    User,
)
from api.services.claim_quality_check_service import (
    CLAIM_QUALITY_CHECK_SWITCH,
)
from api.services.claim_quality_service import (
    ClaimQualityVerdicts,
)
from api.services.claim_quality_warnings import WARNING_TITLES
from api.services.submission_quality_service import QualityVerdict
from api.signals import moderation_event_update_handler_for_opensearch

EVALUATE_PATH = (
    'api.services.claim_quality_check_service.ClaimQualityService.evaluate'
)
CHECK_LOGGER = 'api.services.claim_quality_check_service'
EDIT_SWITCH = 'enable_claim_name_address_edit'


def _verdicts(**flagged):
    fields = {
        warning_type: QualityVerdict(flagged=False, reason='')
        for warning_type in WARNING_TITLES
    }
    for warning_type, reason in flagged.items():
        fields[warning_type] = QualityVerdict(flagged=True, reason=reason)
    return ClaimQualityVerdicts(**fields)


CLEAN_VERDICTS = _verdicts()


class ClaimQualityCheckTestBase(APITestCase):
    def setUp(self):
        # Moderation event propagation to OpenSearch is outside unit
        # tests (the claimed-details PUT records a contribution).
        post_save.disconnect(
            moderation_event_update_handler_for_opensearch, ModerationEvent
        )
        Sector.objects.get_or_create(name='Apparel')

        self.claimant_email = 'claimant@example.com'
        self.password = 'example123'
        self.claimant_user = User.objects.create(email=self.claimant_email)
        self.claimant_user.set_password(self.password)
        self.claimant_user.save()
        self.claimant = Contributor.objects.create(
            admin=self.claimant_user,
            name='Claimant Co',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        list_user = User.objects.create(email='lister@example.com')
        list_contributor = Contributor.objects.create(
            admin=list_user,
            name='List Contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        facility_list = FacilityList.objects.create(
            header='header', file_name='one', name='List'
        )
        source = Source.objects.create(
            facility_list=facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=list_contributor,
        )
        self.list_item = FacilityListItem.objects.create(
            name='Original Name',
            address='1 Original Street',
            country_code='US',
            sector=['Apparel'],
            row_index=1,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=source,
        )
        self.facility = Facility.objects.create(
            name='Original Name',
            address='1 Original Street',
            country_code='US',
            location=Point(0, 0),
            created_from=self.list_item,
        )
        self.list_item.facility = self.facility
        self.list_item.save()
        FacilityMatch.objects.create(
            status=FacilityMatch.CONFIRMED,
            facility=self.facility,
            results='',
            facility_list_item=self.list_item,
        )

    def tearDown(self):
        post_save.connect(
            moderation_event_update_handler_for_opensearch, ModerationEvent
        )

    def login(self):
        self.client.login(
            email=self.claimant_email, password=self.password
        )

    def check_url(self, facility=None):
        facility = facility or self.facility
        return f'/api/facilities/{facility.id}/claim/quality-check/'

    def check(self, **fields):
        return self.client.post(self.check_url(), fields)

    def make_claim(self, **overrides):
        values = {
            'contributor': self.claimant,
            'facility': self.facility,
            'contact_person': 'Claimant',
            'job_title': 'Owner',
            'sector': ['Apparel'],
        }
        values.update(overrides)
        return FacilityClaim.objects.create(**values)

    def valid_form_data(self, **overrides):
        data = {
            'your_name': 'Claimant',
            'your_title': 'Owner',
            'your_business_website': '',
            'business_website': '',
            'business_linkedin_profile':
                'https://www.linkedin.com/company/example',
            'sectors': 'Apparel',
        }
        data.update(overrides)
        return data

    def post_claim(self, **overrides):
        self.login()
        return self.client.post(
            f'/api/facilities/{self.facility.id}/claim/',
            self.valid_form_data(**overrides),
        )

    def put_claimed(self, claim, **fields):
        self.login()
        payload = {
            'facility_name_english': claim.facility_name_english or '',
            'facility_address': claim.facility_address or '',
            'facility_description': '',
            'facility_phone_number_publicly_visible': False,
            'point_of_contact_publicly_visible': False,
            'office_info_publicly_visible': False,
            'facility_website_publicly_visible': False,
        }
        payload.update(fields)
        return self.client.put(
            f'/api/facility-claims/{claim.id}/claimed/',
            payload,
            format='json',
        )

    def make_approved_claim(self):
        return self.make_claim(
            status=FacilityClaimStatuses.APPROVED,
            facility_name_english='Claimed Name',
            facility_address='1 Original Street',
        )


@override_settings(DEBUG=True)
@override_switch('claim_a_facility', active=True)
@override_switch(EDIT_SWITCH, active=True)
@override_switch(CLAIM_QUALITY_CHECK_SWITCH, active=True)
class ClaimQualityCheckEndpointTest(ClaimQualityCheckTestBase):
    '''
    POST /api/facilities/{id}/claim/quality-check/ returns advisory
    warnings for a claimed name and address, never blocks, and calls
    the model only when there is something new to judge.
    '''

    def test_requires_authentication(self):
        response = self.check(
            facility_name_english='New Name', facility_address='2 New St'
        )
        self.assertEqual(401, response.status_code, response.content)

    def test_unknown_facility_is_404(self):
        self.login()
        with patch(EVALUATE_PATH, return_value=CLEAN_VERDICTS) as evaluate:
            response = self.client.post(
                '/api/facilities/XX0000000000000/claim/quality-check/',
                {'facility_name_english': 'New Name'},
            )
        self.assertEqual(404, response.status_code, response.content)
        evaluate.assert_not_called()

    @override_switch('claim_a_facility', active=False)
    def test_claims_switch_off_is_404(self):
        self.login()
        response = self.check(facility_name_english='New Name')
        self.assertEqual(404, response.status_code, response.content)

    @override_switch(EDIT_SWITCH, active=False)
    def test_edit_switch_off_returns_no_warnings_without_a_model_call(self):
        self.login()
        with patch(EVALUATE_PATH, return_value=CLEAN_VERDICTS) as evaluate:
            response = self.check(
                facility_name_english='Test test', facility_address='asdf'
            )
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual({'warnings': []}, response.json())
        evaluate.assert_not_called()

    @override_switch(CLAIM_QUALITY_CHECK_SWITCH, active=False)
    def test_check_switch_off_returns_no_warnings_without_a_model_call(self):
        self.login()
        with patch(EVALUATE_PATH, return_value=CLEAN_VERDICTS) as evaluate:
            response = self.check(
                facility_name_english='Test test', facility_address='asdf'
            )
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual({'warnings': []}, response.json())
        evaluate.assert_not_called()

    def test_unchanged_values_skip_the_model_call(self):
        # Case, surrounding and internal whitespace do not make a value
        # new; the location already lists these, so there is nothing
        # to judge and nothing to pay for.
        self.login()
        with patch(EVALUATE_PATH, return_value=CLEAN_VERDICTS) as evaluate, \
                self.assertLogs(CHECK_LOGGER, level='INFO') as logs:
            response = self.check(
                facility_name_english='  original   NAME ',
                facility_address='1 Original Street',
            )
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual({'warnings': []}, response.json())
        evaluate.assert_not_called()
        self.assertTrue(any(
            'Claim quality check skipped (values unchanged): '
            f'contributor={self.claimant.id} facility={self.facility.id}'
            in line
            for line in logs.output
        ))

    def test_model_is_given_claimed_and_listed_values(self):
        self.login()
        with patch(EVALUATE_PATH, return_value=CLEAN_VERDICTS) as evaluate:
            response = self.check(
                facility_name_english=' New Name ',
                facility_address='1 Original Street',
            )
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual({'warnings': []}, response.json())
        evaluate.assert_called_once_with(
            name='New Name',
            address='1 Original Street',
            country_name='United States',
            current_name='Original Name',
            current_address='1 Original Street',
        )

    def test_flagged_verdicts_become_warnings_in_schema_order(self):
        self.login()
        verdicts = _verdicts(
            different_location='Looks like another city.',
            name_quality='Looks like test data.',
        )
        with patch(EVALUATE_PATH, return_value=verdicts):
            response = self.check(
                facility_name_english='Test test',
                facility_address='9 Elsewhere Road, Othertown',
            )
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual(
            [
                {
                    'type': 'name_quality',
                    'title': WARNING_TITLES['name_quality'],
                    'message': 'Looks like test data.',
                },
                {
                    'type': 'different_location',
                    'title': WARNING_TITLES['different_location'],
                    'message': 'Looks like another city.',
                },
            ],
            response.json()['warnings'],
        )

    def test_model_failure_fails_open(self):
        self.login()
        with patch(EVALUATE_PATH, return_value=None):
            response = self.check(
                facility_name_english='Test test', facility_address='asdf'
            )
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual({'warnings': []}, response.json())

    def test_every_evaluation_logs_the_judged_fields(self):
        # One line per evaluated pair, flagged or not, carrying only
        # the name, address and country: what the model judged and
        # the published record of a location anyway.
        self.login()
        verdicts = _verdicts(address_quality='Too vague.')
        with patch(EVALUATE_PATH, return_value=verdicts), \
                self.assertLogs(CHECK_LOGGER, level='INFO') as logs:
            self.check(
                facility_name_english='New Name', facility_address='asdf'
            )
        evaluated = [
            line for line in logs.output
            if 'Claim quality check evaluated:' in line
        ]
        self.assertEqual(1, len(evaluated))
        self.assertIn(
            f'contributor={self.claimant.id} facility={self.facility.id} '
            "warnings=['address_quality'] fields=",
            evaluated[0],
        )
        fields = json.loads(evaluated[0].split('fields=', 1)[1])
        self.assertEqual(
            {'name': 'New Name', 'address': 'asdf', 'country': 'US'},
            fields,
        )

    def test_over_long_value_is_rejected(self):
        self.login()
        with patch(EVALUATE_PATH, return_value=CLEAN_VERDICTS) as evaluate:
            response = self.check(facility_name_english='a' * 201)
        self.assertEqual(400, response.status_code, response.content)
        self.assertIn('facility_name_english', response.json())
        evaluate.assert_not_called()
