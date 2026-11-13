from django.core.cache import cache
from django.test import TestCase

from api.constants import PARTNER_FIELD_LIST_KEY
from api.models.partner_field import PartnerField
from api.serializers.facility.partner_field_helper import (
    get_cached_all_partner_fields,
)


class PartnerFieldCacheInvalidationTest(TestCase):
    """`PartnerField.save` drops the cached field list on every save
    (OSDEV-3778), so an admin edit to any attribute, not only `active`,
    is what the next facility details read serializes."""

    def setUp(self):
        cache.delete(PARTNER_FIELD_LIST_KEY)
        self.field = PartnerField.objects.create(
            name='cache_test_field',
            type=PartnerField.STRING,
            label='Cache Test Field',
        )

    def tearDown(self):
        cache.delete(PARTNER_FIELD_LIST_KEY)

    def _cached_field(self):
        return next(
            field for field in get_cached_all_partner_fields()
            if field.pk == self.field.pk
        )

    def test_beta_edit_is_visible_on_the_next_read(self):
        self.assertIs(self._cached_field().beta, False)

        self.field.beta = True
        self.field.save()

        self.assertIs(self._cached_field().beta, True)

    def test_label_edit_is_visible_on_the_next_read(self):
        self.assertEqual(self._cached_field().label, 'Cache Test Field')

        self.field.label = 'Renamed Field'
        self.field.save()

        self.assertEqual(self._cached_field().label, 'Renamed Field')

    def test_active_flip_still_invalidates(self):
        self.assertIs(self._cached_field().active, True)

        self.field.active = False
        self.field.save()

        self.assertIs(self._cached_field().active, False)
