from api.admin import FacilityCandidateFilter, admin_site
from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityAlias,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    FacilityMatch,
    Source,
    User,
)
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, Point
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

CANDIDATE_POLYGON_WKT = 'POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'

# Admin templates resolve static URLs through the manifest storage, which
# needs a collectstatic run the test suite does not do. Render them with
# the plain storage instead.
TEST_STORAGES = {
    **settings.STORAGES,
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


@override_settings(STORAGES=TEST_STORAGES)
class FacilityAdminCandidateTest(TestCase):
    """Django admin treatment of candidate facilities (OSDEV-3379).

    Candidates are absent from the Facility changelist unless staff opt in
    through the candidate status filter, are badged wherever they appear,
    and are view-only in the change, delete and history views.
    """

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email='super@example.com', password='example123'
        )
        self.client.force_login(self.superuser)

        self.user = User.objects.create(email='one@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='test contributor 1',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )
        guard_settings = override_settings(
            EARTH_GENOME_CONTRIBUTOR_ID=self.contributor.id
        )
        guard_settings.enable()
        self.addCleanup(guard_settings.disable)
        self.list = FacilityList.objects.create(
            header='header', file_name='one', name='First List'
        )
        self.source = Source.objects.create(
            facility_list=self.list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        self.next_row_index = 0

        self.facility = self._create_facility(name='Confirmed')
        self.candidate = self._create_candidate()

    def _create_list_item(self):
        self.next_row_index += 1
        return FacilityListItem.objects.create(
            name='Item',
            address='Address',
            country_code='US',
            sector=['Apparel'],
            row_index=self.next_row_index,
            geocoded_point=Point(0, 0),
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )

    def _create_facility(self, **kwargs):
        defaults = {
            'name': 'Name',
            'address': 'Address',
            'country_code': 'US',
            'location': Point(0, 0),
            'created_from': self._create_list_item(),
        }
        defaults.update(kwargs)
        return Facility.including_candidates.create(**defaults)

    def _create_candidate(self, **kwargs):
        defaults = {
            'name': '',
            'address': '',
            'is_candidate': True,
            'polygon': GEOSGeometry(CANDIDATE_POLYGON_WKT, srid=4326),
            'confidence': 0.87,
            'external_id': 'eg-facility-0001',
            'source': 'earth_genome',
        }
        defaults.update(kwargs)
        return self._create_facility(**defaults)

    @staticmethod
    def _changelist_ids(response):
        return {f.id for f in response.context['cl'].result_list}

    @staticmethod
    def _filter_choices(response):
        cl = response.context['cl']
        spec = next(
            s for s in cl.filter_specs
            if isinstance(s, FacilityCandidateFilter)
        )
        return list(spec.choices(cl))

    def _admin_url(self, name, *args):
        return reverse('admin:api_facility_{}'.format(name), args=args)

    # --- AC #1: changelist ------------------------------------------------

    def test_changelist_excludes_candidates_by_default(self):
        response = self.client.get(self._admin_url('changelist'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._changelist_ids(response), {self.facility.id})
        self.assertNotContains(response, self.candidate.id)

    def test_default_filter_choice_is_confirmed_only(self):
        response = self.client.get(self._admin_url('changelist'))

        choices = self._filter_choices(response)
        self.assertEqual(
            [c['display'] for c in choices],
            ['Confirmed only', 'Candidates only', 'All'],
        )
        selected = [c['display'] for c in choices if c['selected']]
        self.assertEqual(selected, ['Confirmed only'])
        # No choice clears the parameter: every link carries an explicit
        # value, so there is no way back to an unfiltered default.
        for choice in choices:
            self.assertIn('candidate=', choice['query_string'])

    def test_candidates_only_filter_shows_candidate_badged(self):
        response = self.client.get(
            self._admin_url('changelist'),
            {FacilityCandidateFilter.parameter_name:
             FacilityCandidateFilter.CANDIDATES},
        )

        self.assertEqual(self._changelist_ids(response), {self.candidate.id})
        self.assertContains(response, self.candidate.id)
        # The is_candidate boolean column renders Django's "yes" icon for
        # the candidate row and no "no" icon, since every row shown is
        # a candidate.
        self.assertContains(response, 'icon-yes.svg')
        self.assertNotContains(response, 'icon-no.svg')

    def test_all_filter_shows_both_and_badges_only_the_candidate(self):
        response = self.client.get(
            self._admin_url('changelist'),
            {FacilityCandidateFilter.parameter_name:
             FacilityCandidateFilter.ALL},
        )

        self.assertEqual(
            self._changelist_ids(response),
            {self.facility.id, self.candidate.id},
        )
        self.assertContains(response, 'icon-yes.svg', count=1)
        self.assertContains(response, 'icon-no.svg', count=1)

    def test_unknown_filter_value_falls_back_to_confirmed_only(self):
        response = self.client.get(
            self._admin_url('changelist'),
            {FacilityCandidateFilter.parameter_name: 'bogus'},
        )

        self.assertEqual(self._changelist_ids(response), {self.facility.id})

    # --- Change / history / delete views ---------------------------------

    def test_candidate_change_view_is_read_only(self):
        response = self.client.get(
            self._admin_url('change', self.candidate.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_change_permission'])
        self.assertFalse(response.context['has_delete_permission'])
        self.assertNotContains(response, 'name="_save"')
        self.assertEqual(response.context['adminform'].form.fields, {})
        self.assertContains(response, 'eg-facility-0001')

    def test_candidate_change_view_rejects_post(self):
        response = self.client.post(
            self._admin_url('change', self.candidate.id),
            {'name': 'Renamed', 'address': 'A', 'country_code': 'US'},
        )

        self.assertEqual(response.status_code, 403)
        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.name, '')

    def test_candidate_delete_view_is_forbidden(self):
        response = self.client.get(
            self._admin_url('delete', self.candidate.id)
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Facility.including_candidates.filter(
                pk=self.candidate.id
            ).exists()
        )

    def test_candidate_history_view_resolves(self):
        response = self.client.get(
            self._admin_url('history', self.candidate.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.candidate.id)

    def test_confirmed_facility_stays_editable(self):
        response = self.client.get(
            self._admin_url('change', self.facility.id)
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_change_permission'])
        self.assertContains(response, 'name="_save"')
        form_fields = response.context['adminform'].form.fields
        self.assertIn('name', form_fields)
        # Candidate state and ingest identity are never editable through
        # the admin, on any facility.
        for name in ('is_candidate', 'source', 'external_id'):
            self.assertNotIn(name, form_fields)

    # --- Other admins that point at Facility -----------------------------

    def test_facility_fks_on_other_admins_are_read_only(self):
        """
        Admin FK form fields build their choices from Facility.objects,
        which cannot see a candidate, so an editable Facility FK would make
        saving a candidate-linked row fail with "select a valid choice".
        Every registered admin whose model points at Facility must keep
        that FK out of its form.
        """
        request = RequestFactory().get('/admin/')
        request.user = self.superuser
        checked = set()

        for model, model_admin in admin_site._registry.items():
            if model is Facility:
                continue
            fk_names = [
                f.name for f in model._meta.get_fields()
                if f.concrete and (f.many_to_one or f.one_to_one)
                and f.related_model is Facility
            ]
            if not fk_names:
                continue
            form_fields = model_admin.get_form(request)().fields
            for name in fk_names:
                self.assertNotIn(
                    name, form_fields,
                    '{}.{} is an editable Facility FK in the admin'.format(
                        model.__name__, name
                    ),
                )
            checked.add(model)

        self.assertTrue(
            {FacilityClaim, FacilityMatch, FacilityListItem, FacilityAlias,
             ExtendedField} <= checked,
            checked,
        )
