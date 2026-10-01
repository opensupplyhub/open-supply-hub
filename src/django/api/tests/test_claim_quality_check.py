import json
from unittest.mock import patch

from django.contrib.gis.geos import Point
from django.core.cache import caches
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
        # DuplicateThrottle keys on user id + body in the shared
        # 'api_throttling' cache, which outlives a test run; the test DB
        # reuses ids, so a stale entry would turn a first request into a
        # spurious 429.
        caches['api_throttling'].clear()

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

    def test_model_failure_fails_open_and_logs_as_failed(self):
        # The evaluated line still appears, marked model=failed, so an
        # empty warnings list from a fail-open failure can be told from
        # a clean verdict when watching the false-positive rate.
        self.login()
        with patch(EVALUATE_PATH, return_value=None), \
                self.assertLogs(CHECK_LOGGER, level='INFO') as logs:
            response = self.check(
                facility_name_english='Test test', facility_address='asdf'
            )
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual({'warnings': []}, response.json())
        self.assertTrue(any(
            f'contributor={self.claimant.id} facility={self.facility.id} '
            'model=failed warnings=[] fields='
            in line
            for line in logs.output
        ))

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
            "model=ok warnings=['address_quality'] fields=",
            evaluated[0],
        )
        fields = json.loads(evaluated[0].split('fields=', 1)[1])
        self.assertEqual(
            {'name': 'New Name', 'address': 'asdf', 'country': 'US'},
            fields,
        )

    def test_over_long_value_is_rejected(self):
        self.login()
        for field in ('facility_name_english', 'facility_address'):
            with self.subTest(field=field), \
                    patch(EVALUATE_PATH, return_value=CLEAN_VERDICTS) \
                    as evaluate:
                response = self.check(**{field: 'a' * 201})
            self.assertEqual(400, response.status_code, response.content)
            self.assertIn(field, response.json())
            evaluate.assert_not_called()

    def test_approved_claim_values_are_the_baseline(self):
        # Approval records the claimed name as a contribution but never
        # rewrites facility.name, while the location page and the
        # claimed-details form show the claimed name. Re-asserting it
        # is nothing new, so no model call: otherwise every save of an
        # approved claim would be judged against the stale listing.
        self.make_approved_claim()
        self.login()
        with patch(EVALUATE_PATH, return_value=CLEAN_VERDICTS) as evaluate:
            response = self.check(
                facility_name_english='Claimed Name',
                facility_address='1 Original Street',
            )
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual({'warnings': []}, response.json())
        evaluate.assert_not_called()

    def test_model_is_given_the_approved_claim_values_as_listed(self):
        self.make_approved_claim()
        self.login()
        with patch(EVALUATE_PATH, return_value=CLEAN_VERDICTS) as evaluate:
            self.check(
                facility_name_english='Renamed Co',
                facility_address='1 Original Street',
            )
        evaluate.assert_called_once_with(
            name='Renamed Co',
            address='1 Original Street',
            country_name='United States',
            current_name='Claimed Name',
            current_address='1 Original Street',
        )

    def test_blank_values_stand_for_the_listed_ones(self):
        # A blank asserts nothing, the way the write path backfills a
        # blank from the location, so an empty body or a blank field
        # is not judged and `address_quality` is never asked about ''.
        self.login()
        for body in ({}, {'facility_name_english': '',
                          'facility_address': ''}):
            with self.subTest(body=body), \
                    patch(EVALUATE_PATH, return_value=CLEAN_VERDICTS) \
                    as evaluate:
                response = self.client.post(self.check_url(), body)
            self.assertEqual(200, response.status_code, response.content)
            self.assertEqual({'warnings': []}, response.json())
            evaluate.assert_not_called()

        with patch(EVALUATE_PATH, return_value=CLEAN_VERDICTS) as evaluate:
            self.check(facility_name_english='New Name')
        evaluate.assert_called_once_with(
            name='New Name',
            address='1 Original Street',
            country_name='United States',
            current_name='Original Name',
            current_address='1 Original Street',
        )

    def test_unchanged_is_judged_the_way_the_write_path_judges_it(self):
        # The write path treats '1 Original St.' and '1 Original St' as
        # the same address (no geocode); the check must agree, or it
        # pays for a model call and warns about an edit the write
        # ignores.
        self.facility.address = '1 Original St.'
        self.facility.save()
        self.login()
        with patch(EVALUATE_PATH, return_value=CLEAN_VERDICTS) as evaluate:
            response = self.check(
                facility_name_english='Original Name',
                facility_address='1 Original St',
            )
        self.assertEqual({'warnings': []}, response.json())
        evaluate.assert_not_called()

    def test_single_field_verdicts_are_not_reported_for_listed_value(self):
        # A name-only correction must not warn about the listing's own
        # address (nor an address-only one about the listing's name);
        # the pairwise verdicts are still reported.
        self.login()
        verdicts = _verdicts(
            name_quality='Looks like test data.',
            address_quality='Too vague.',
            address_country_mismatch='Not in the US.',
            different_location='Looks like another city.',
        )
        with patch(EVALUATE_PATH, return_value=verdicts):
            response = self.check(
                facility_name_english='Test test',
                facility_address='1 Original Street',
            )
        self.assertEqual(
            ['name_quality', 'different_location'],
            [warning['type'] for warning in response.json()['warnings']],
        )

        with patch(EVALUATE_PATH, return_value=verdicts):
            response = self.check(
                facility_name_english='Original Name',
                facility_address='Guangdong Province',
            )
        self.assertEqual(
            ['address_quality', 'address_country_mismatch',
             'different_location'],
            [warning['type'] for warning in response.json()['warnings']],
        )

    def test_warning_vocabulary_matches_the_verdict_schema(self):
        self.assertEqual(
            set(WARNING_TITLES),
            set(ClaimQualityVerdicts.model_fields),
        )

    def test_unknown_warning_type_is_skipped_not_raised(self):
        # If the vocabulary ever gains an entry the schema lacks, the
        # endpoint must still answer (fail open) with the warnings it
        # can map.
        self.login()
        titles = dict(WARNING_TITLES, not_a_verdict='Not A Verdict')
        verdicts = _verdicts(name_quality='Looks like test data.')
        with patch(
            'api.services.claim_quality_check_service.WARNING_TITLES',
            titles,
        ), patch(EVALUATE_PATH, return_value=verdicts):
            response = self.check(
                facility_name_english='Test test',
                facility_address='9 Elsewhere Road',
            )
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual(
            ['name_quality'],
            [warning['type'] for warning in response.json()['warnings']],
        )

    def test_identical_repeat_is_throttled_without_a_model_call(self):
        self.login()
        body = {
            'facility_name_english': 'New Name',
            'facility_address': '9 Elsewhere Road',
        }
        with patch(EVALUATE_PATH, return_value=CLEAN_VERDICTS) as evaluate:
            first = self.client.post(self.check_url(), body)
            second = self.client.post(self.check_url(), body)
        self.assertEqual(200, first.status_code, first.content)
        self.assertEqual(429, second.status_code, second.content)
        evaluate.assert_called_once()
