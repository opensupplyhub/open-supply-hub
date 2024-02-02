from django.db.models import (
    Model,
    BigAutoField,
    ForeignKey,
    CharField,
    JSONField,
    IntegerField,
    DateTimeField,
    Index,
    CASCADE,
)

from api.models.facility.field_type import FieldType


class FacilityListItemField(Model):
    class Meta:
        unique_together = [['facility_list_item_id', 'key']]
        indexes = [
            Index(fields=['facility_list_item_id', 'key'],
                  name='facility_list_item_id_key_idx'),
        ]

    id = BigAutoField(
        auto_created=True,
        primary_key=True,
        serialize=False
    )
    facility_list_item = ForeignKey(
        'FacilityListItem',
        null=False,
        # on deletion of FacilityListItem deletes its FacilityListItemField-s
        on_delete=CASCADE,
        help_text='The facility list item which this field belongs to.'
    )
    key = CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text='Name of the field for facility list item.')
    value = JSONField(
        null=False,
        blank=False,
        help_text='Content of the field for facility list item.')
    type = IntegerField(choices=FieldType.choices)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f'FacilityListItemField {self.id} - {self.key} - {self.value}'
