from django.test import SimpleTestCase

from api.serializers.facility.facility_index_extended_field_list_serializer \
    import FacilityIndexExtendedFieldListSerializer


def make_extended_field(**overrides):
    field = {
        'id': 1,
        'is_verified': False,
        'value': {'raw_value': 'value'},
        'created_at': '2026-01-01T00:00:00Z',
        'updated_at': '2026-01-02T00:00:00Z',
        'contributor': {
            'id': 10,
            'admin_id': 100,
            'name': 'A Contributor',
            'contrib_type': 'Brand/Retailer',
            'is_verified': False,
        },
        'facility_list_item_id': 55,
        'field_name': 'number_of_workers',
        'should_display_association': True,
    }
    field.update(overrides)
    return field


def serialize_one(extended_field, context_overrides=None):
    context = {
        'user_can_see_detail': True,
        'embed_mode_active': False,
        'masked_contributor_ids': set(),
    }
    context.update(context_overrides or {})
    serializer = FacilityIndexExtendedFieldListSerializer(
        [extended_field],
        context=context,
    )
    return serializer.data[0]


class IsFromClaimTest(SimpleTestCase):
    """The claimed badge (is_from_claim) recognizes claimant data from
    every channel, not only fields created directly on the claim."""

    def test_claim_created_field_is_from_claim(self):
        # Fields created from a FacilityClaim have no list item.
        data = serialize_one(make_extended_field(facility_list_item_id=None))
        self.assertTrue(data['is_from_claim'])

    def test_claimant_list_contribution_is_from_claim(self):
        # The approved claimant contributed this field via SLC/list upload.
        data = serialize_one(
            make_extended_field(),
            context_overrides={'claimant_contributor_id': 10},
        )
        self.assertTrue(data['is_from_claim'])

    def test_other_contributor_field_is_not_from_claim(self):
        data = serialize_one(
            make_extended_field(),
            context_overrides={'claimant_contributor_id': 999},
        )
        self.assertFalse(data['is_from_claim'])

    def test_unclaimed_facility_field_is_not_from_claim(self):
        # No claimant in context (unclaimed facility, or callers that do
        # not resolve a claim) keeps the previous behavior.
        data = serialize_one(make_extended_field())
        self.assertFalse(data['is_from_claim'])
