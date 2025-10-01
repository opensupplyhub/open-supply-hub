from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from unittest.mock import Mock

from api.models import (
    Contributor,
    ExtendedField,
    Facility,
    FacilityList,
    FacilityListItem,
    Source,
)
from api.admin import SourceAdmin

User = get_user_model()


class SourceContributorChangeTest(TestCase):
    """
    Test that changing a Source's contributor updates related ExtendedFields.
    This addresses OSDEV-2159: Extended fields retain original contributor
    after list source reassignment.
    """

    def setUp(self):
        # Create admin user
        self.admin_email = "admin@example.com"
        self.admin_user = User.objects.create_superuser(
            email=self.admin_email, password="password"
        )

        # Create original contributor
        self.original_contrib_email = "original@example.com"
        self.original_user = User.objects.create(email=self.original_contrib_email)
        self.original_contributor = Contributor.objects.create(
            admin=self.original_user,
            name="Original Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        # Create new contributor to transfer to
        self.new_contrib_email = "new@example.com"
        self.new_user = User.objects.create(email=self.new_contrib_email)
        self.new_contributor = Contributor.objects.create(
            admin=self.new_user,
            name="New Contributor",
            contrib_type=Contributor.OTHER_CONTRIB_TYPE,
        )

        # Create facility
        self.facility = Facility.objects.create(
            name="Test Facility",
            address="123 Test St",
            country_code="US",
            location="POINT(0 0)",
            created_from_id=1,
        )

        # Create facility list
        self.facility_list = FacilityList.objects.create(
            name="Test List",
            description="Test list for contributor change",
            file_name="test.csv",
            header="name,address,country",
        )

        # Create source with original contributor
        self.source = Source.objects.create(
            source_type=Source.LIST,
            contributor=self.original_contributor,
            facility_list=self.facility_list,
        )

        # Create facility list item
        self.list_item = FacilityListItem.objects.create(
            source=self.source,
            row_index=1,
            raw_data="Test Facility,123 Test St,US",
            raw_header="name,address,country",
            raw_json={
                "name": "Test Facility",
                "address": "123 Test St",
                "country": "US",
            },
            name="Test Facility",
            address="123 Test St",
            country_code="US",
            clean_name="test facility",
            clean_address="123 test st",
            facility=self.facility,
            status=FacilityListItem.MATCHED,
        )

        # Create extended field linked to original contributor
        self.extended_field = ExtendedField.objects.create(
            contributor=self.original_contributor,
            facility=self.facility,
            facility_list_item=self.list_item,
            field_name=ExtendedField.NUMBER_OF_WORKERS,
            value={"min": 100, "max": 500},
        )

        # Create another extended field to test multiple updates
        self.extended_field_2 = ExtendedField.objects.create(
            contributor=self.original_contributor,
            facility=self.facility,
            facility_list_item=self.list_item,
            field_name=ExtendedField.NATIVE_LANGUAGE_NAME,
            value="Test Factory",
        )

        # Set up admin
        self.site = AdminSite()
        self.source_admin = SourceAdmin(Source, self.site)

    def test_changing_source_contributor_updates_extended_fields(self):
        """Test that changing a Source's contributor updates all related ExtendedFields."""
        # Verify initial state
        self.assertEqual(self.extended_field.contributor, self.original_contributor)
        self.assertEqual(self.extended_field_2.contributor, self.original_contributor)

        # Create mock request and form
        request = Mock()
        request.user = self.admin_user
        messages_list = []

        def mock_message_user(req, msg, level=None):
            messages_list.append(msg)

        self.source_admin.message_user = mock_message_user

        # Create mock form with changed_data
        form = Mock()
        form.changed_data = ['contributor']

        # Change the contributor
        self.source.contributor = self.new_contributor

        # Call save_model
        self.source_admin.save_model(request, self.source, form, change=True)

        # Refresh extended fields from database
        self.extended_field.refresh_from_db()
        self.extended_field_2.refresh_from_db()

        # Verify extended fields now have new contributor
        self.assertEqual(self.extended_field.contributor, self.new_contributor)
        self.assertEqual(self.extended_field_2.contributor, self.new_contributor)

        # Verify message was sent
        self.assertEqual(len(messages_list), 1)
        self.assertIn("Updated 2 extended field(s)", messages_list[0])
        self.assertIn(str(self.new_contributor), messages_list[0])

    def test_saving_source_without_contributor_change_does_not_update_extended_fields(self):
        """Test that saving a Source without changing contributor doesn't affect ExtendedFields."""
        # Create mock request and form
        request = Mock()
        request.user = self.admin_user

        # Create mock form with no contributor in changed_data
        form = Mock()
        form.changed_data = ['is_active']  # Some other field changed

        # Change something else on the source
        self.source.is_active = False

        # Call save_model
        self.source_admin.save_model(request, self.source, form, change=True)

        # Refresh extended fields from database
        self.extended_field.refresh_from_db()
        self.extended_field_2.refresh_from_db()

        # Verify extended fields still have original contributor
        self.assertEqual(self.extended_field.contributor, self.original_contributor)
        self.assertEqual(self.extended_field_2.contributor, self.original_contributor)

    def test_creating_new_source_does_not_trigger_extended_field_update(self):
        """Test that creating a new Source doesn't trigger ExtendedField updates."""
        # Create new source
        new_list = FacilityList.objects.create(
            name="New List",
            description="New test list",
            file_name="new.csv",
            header="name,address,country",
        )

        new_source = Source(
            source_type=Source.LIST,
            contributor=self.new_contributor,
            facility_list=new_list,
        )

        # Create mock request and form
        request = Mock()
        request.user = self.admin_user
        form = Mock()
        form.changed_data = ['contributor', 'source_type', 'facility_list']

        # Call save_model for new object (change=False)
        self.source_admin.save_model(request, new_source, form, change=False)

        # Verify original extended fields unchanged
        self.extended_field.refresh_from_db()
        self.extended_field_2.refresh_from_db()
        self.assertEqual(self.extended_field.contributor, self.original_contributor)
        self.assertEqual(self.extended_field_2.contributor, self.original_contributor)

    def test_extended_fields_without_list_item_are_not_affected(self):
        """Test that ExtendedFields from claims (without list items) are not affected."""
        # Create an extended field from a claim (no list item)
        claim_extended_field = ExtendedField.objects.create(
            contributor=self.original_contributor,
            facility=self.facility,
            facility_list_item=None,  # No list item - this is from a claim
            field_name=ExtendedField.PARENT_COMPANY,
            value="Parent Corp",
        )

        # Change the source contributor
        request = Mock()
        request.user = self.admin_user
        form = Mock()
        form.changed_data = ['contributor']
        self.source.contributor = self.new_contributor

        self.source_admin.save_model(request, self.source, form, change=True)

        # Verify claim-based extended field is not changed
        claim_extended_field.refresh_from_db()
        self.assertEqual(claim_extended_field.contributor, self.original_contributor)

        # But list-based extended fields should be updated
        self.extended_field.refresh_from_db()
        self.assertEqual(self.extended_field.contributor, self.new_contributor)