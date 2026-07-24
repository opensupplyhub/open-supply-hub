from datetime import date, timedelta

from django.contrib.gis.geos import Point
from django.test import TestCase

from api.constants import FacilityClaimStatuses
from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityClaim,
    FacilityList,
    FacilityListItem,
    Source,
    User,
)
from api.services.change_intelligence_name_normalization import name_changed
from api.services.change_intelligence_report import (
    get_change_intelligence_report,
)

# `history_date` is set to `timezone.now()` at save time, so the "in window"
# bound must be relative to test-run time, not a fixed calendar date, or this
# suite would start failing the moment wall-clock time moves past a
# hardcoded window.
IN_WINDOW = (
    date.today() - timedelta(days=1), date.today() + timedelta(days=1)
)
OUT_OF_WINDOW = (date(2020, 1, 1), date(2020, 12, 31))


class NameChangedTest(TestCase):
    """Regression cases from the validated OSDEV-2903 POC self-check --
    formatting/legal-suffix variants must not read as a rename."""

    def test_prefix_and_formatting_variant_not_changed(self):
        self.assertFalse(name_changed(
            'M/S. INDOCHINE APPAREL(BANGLADESH) LIMITED.',
            'INDOCHINE APPAREL (BANGLADESH) LIMITED',
        ))

    def test_suffix_variant_not_changed(self):
        self.assertFalse(
            name_changed('Odessa Fashions Limited', 'Odessa Fashions Ltd')
        )

    def test_punctuation_variant_not_changed(self):
        self.assertFalse(name_changed(
            'Mastrade International Garments Ltd',
            'Mastrade International Garments Ltd.',
        ))

    def test_case_and_punctuation_variant_not_changed(self):
        self.assertFalse(name_changed(
            'Thanbee print world ltd', 'Thanbee Print World Ltd.',
        ))

    def test_real_rename_is_changed(self):
        self.assertTrue(
            name_changed('Agami Washing Ltd.', 'Agami Fashions Ltd.')
        )


class GetChangeIntelligenceReportTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='claimant@example.com')
        self.contributor = Contributor.objects.create(
            admin=self.user,
            name='Test Contributor',
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        self.facility_list = FacilityList.objects.create(
            header='header', file_name='list', name='List',
        )
        self.source = Source.objects.create(
            facility_list=self.facility_list,
            source_type=Source.LIST,
            is_active=True,
            is_public=True,
            contributor=self.contributor,
        )
        self.list_item = FacilityListItem.objects.create(
            name='Original Name',
            address='Original Address',
            country_code='US',
            sector=['Apparel'],
            row_index=1,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )

        self.facility = Facility.objects.create(
            name='Original Name',
            address='Original Address',
            country_code='US',
            location=Point(0, 0),
            created_from=self.list_item,
        )

        self.other_list_item = FacilityListItem.objects.create(
            name='Other Facility',
            address='Other Address',
            country_code='US',
            sector=['Apparel'],
            row_index=2,
            status=FacilityListItem.CONFIRMED_MATCH,
            source=self.source,
        )
        self.other_facility = Facility.objects.create(
            name='Other Facility',
            address='Other Address',
            country_code='US',
            location=Point(0, 0),
            created_from=self.other_list_item,
        )

    def _report(self, os_ids, window=IN_WINDOW):
        return get_change_intelligence_report(os_ids, window[0], window[1])

    def test_claimed_status_signal(self):
        claim = FacilityClaim.objects.create(
            contributor=self.contributor,
            facility=self.facility,
            contact_person='Name',
            company_name='Test',
            website='http://example.com',
            facility_description='description',
            status=FacilityClaimStatuses.PENDING,
        )
        claim.status = FacilityClaimStatuses.APPROVED
        claim.save()

        rows = self._report([self.facility.id])
        claim_rows = [r for r in rows if r['Change Type'] == 'Claimed status']

        self.assertEqual(len(claim_rows), 1)
        row = claim_rows[0]
        self.assertEqual(row['OS ID'], self.facility.id)
        self.assertEqual(row['Previous Value'], FacilityClaimStatuses.PENDING)
        self.assertEqual(row['New Value'], FacilityClaimStatuses.APPROVED)
        self.assertEqual(row['Claimed Status'], 'Claimed')
        self.assertEqual(
            row['Suggested Next Action'], 'Review claim / verify operator'
        )

    def test_material_facility_type_signal(self):
        field = ExtendedField.objects.create(
            facility=self.facility,
            contributor=self.contributor,
            field_name=ExtendedField.FACILITY_TYPE,
            value={'raw_values': ['Weaving']},
        )
        field.value = {'raw_values': ['Dyeing']}
        field.save()

        rows = self._report([self.facility.id])
        material_rows = [
            r for r in rows if r['Change Type'] == 'Material facility'
        ]

        self.assertEqual(len(material_rows), 1)
        self.assertEqual(material_rows[0]['Field Changed'], 'facility_type')
        self.assertEqual(
            material_rows[0]['Suggested Next Action'],
            'Re-assess sourcing relevance',
        )

    def test_other_extended_field_names_are_not_material_signal(self):
        field = ExtendedField.objects.create(
            facility=self.facility,
            contributor=self.contributor,
            field_name=ExtendedField.PROCESSING_TYPE,
            value={'raw_values': ['Cut']},
        )
        field.value = {'raw_values': ['Sew']}
        field.save()

        rows = self._report([self.facility.id])
        self.assertEqual(
            [r for r in rows if r['Change Type'] == 'Material facility'], []
        )

    def test_address_signal(self):
        self.facility.address = 'New Address'
        self.facility.save()

        rows = self._report([self.facility.id])
        address_rows = [
            r for r in rows if r['Field Changed'] == 'address'
        ]

        self.assertEqual(len(address_rows), 1)
        self.assertEqual(address_rows[0]['Previous Value'], 'Original Address')
        self.assertEqual(address_rows[0]['New Value'], 'New Address')

    def test_real_name_change_produces_a_row(self):
        self.facility.name = 'Renamed Facility'
        self.facility.save()

        rows = self._report([self.facility.id])
        name_rows = [r for r in rows if r['Field Changed'] == 'name']

        self.assertEqual(len(name_rows), 1)
        self.assertEqual(name_rows[0]['New Value'], 'Renamed Facility')

    def test_formatting_only_name_change_produces_no_row(self):
        self.facility.name = 'Original Name.'
        self.facility.save()

        rows = self._report([self.facility.id])
        self.assertEqual([r for r in rows if r['Field Changed'] == 'name'], [])

    def test_watchlist_scoping_excludes_other_facilities(self):
        self.other_facility.name = 'Renamed Other Facility'
        self.other_facility.save()

        rows = self._report([self.facility.id])
        self.assertEqual(
            [r for r in rows if r['OS ID'] == self.other_facility.id], []
        )

    def test_date_window_excludes_changes_outside_range(self):
        self.facility.name = 'Renamed Facility'
        self.facility.save()

        rows = self._report([self.facility.id], window=OUT_OF_WINDOW)
        self.assertEqual(rows, [])

    def test_empty_watchlist_returns_empty_list_without_error(self):
        self.assertEqual(self._report([]), [])

    def test_claimed_status_column_for_unclaimed_facility(self):
        self.facility.name = 'Renamed Facility'
        self.facility.save()

        rows = self._report([self.facility.id])
        self.assertTrue(rows)
        self.assertTrue(all(r['Claimed Status'] == 'Unclaimed' for r in rows))

    def test_placeholder_columns_are_always_empty(self):
        self.facility.name = 'Renamed Facility'
        self.facility.save()

        rows = self._report([self.facility.id])
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual(row['DUNS'], '')
            self.assertEqual(row['LEI'], '')
            self.assertEqual(row['GLN'], '')
            self.assertEqual(row['Tier'], '')
            self.assertEqual(row['Confidence Level'], '')
