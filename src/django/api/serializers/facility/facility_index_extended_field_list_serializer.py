from typing import Union

from ..utils import is_contribution_masked
from .utils import (
    get_contributor_name_from_facilityindex,
    get_contributor_id_from_facilityindex,
    format_date
)


class FacilityIndexExtendedFieldListSerializer:
    def __init__(self,
                 extended_field_list: list,
                 context: dict,
                 exclude_fields: list = []) -> None:
        self.extended_field_list = extended_field_list
        self.context = context
        # The masked set is the same for every field in the list, so resolve
        # it once instead of re-reading it from the context for each field's
        # contributor_name and contributor_id.
        self.masked_contributors = context.get('masked_contributor_ids')

        self.fields: list = ['id', 'is_verified', 'value', 'created_at',
                             'updated_at', 'contributor_name',
                             'contributor_id', 'value_count', 'is_from_claim',
                             'field_name', 'verified_count', 'source_by',
                             'unit', 'label', 'base_url', 'display_text',
                             'json_schema']
        self.data: list = []

        if exclude_fields:
            for field_name in exclude_fields:
                self.fields.remove(field_name)

        self._serialize_extended_field_list()

    def _serialize_extended_field_list(self) -> None:
        field_serializers = {
            'created_at': self._get_created_at,
            'updated_at': self._get_updated_at,
            'contributor_name': self._get_contributor_name,
            'contributor_id': self._get_contributor_id,
            'is_from_claim': self._get_is_from_claim,
            'verified_count': self._get_verified_count,
        }
        context_overrides = {
            'source_by',
            'unit',
            'label',
            'base_url',
            'display_text',
            'json_schema'
        }

        for extended_field in self.extended_field_list:
            serialized_extended_field = {}

            for field in self.fields:
                if field in field_serializers:
                    serialized_extended_field[field] = \
                        field_serializers[field](
                            extended_field
                        )
                    continue

                if field in context_overrides:
                    context_value = self.context.get(field)
                    if context_value is not None:
                        serialized_extended_field[field] = context_value
                        continue

                serialized_extended_field[field] = extended_field.get(field)

            self.data.append(serialized_extended_field)

    def _should_display_contributor(self, extended_field: dict) -> bool:
        user_can_see_detail = self.context.get('user_can_see_detail')
        should_display_association = extended_field.get(
            'should_display_association')

        return should_display_association and user_can_see_detail

    def _get_contributor_name(self, extended_field: dict) -> Union[None, str]:
        embed_mode_active = self.context.get('embed_mode_active')
        if embed_mode_active:
            return None
        return get_contributor_name_from_facilityindex(
            extended_field.get('contributor'),
            self._should_display_contributor(extended_field),
            self.masked_contributors)

    def _get_contributor_id(self, extended_field: dict) -> Union[None, int]:
        embed_mode_active = self.context.get('embed_mode_active')
        if embed_mode_active:
            return None
        return get_contributor_id_from_facilityindex(
            extended_field.get('contributor'),
            self._should_display_contributor(extended_field),
            self.masked_contributors
        )

    def _get_is_from_claim(self, extended_field: dict) -> bool:
        # Fields created directly from a FacilityClaim have no list item.
        if extended_field.get('facility_list_item_id') is None:
            return True
        # Fields the approved claimant contributed through other channels
        # (SLC, list upload) are also claimant data. See the Promotion
        # Logic Q3 plan.
        claimant_contributor_id = self.context.get('claimant_contributor_id')
        if claimant_contributor_id is None:
            return False
        contributor = extended_field.get('contributor') or {}
        # A masked (anonymized) contribution must not be attributed to the
        # claim: the claimant is publicly named, so the badge would undo
        # the masking by inference.
        if is_contribution_masked(contributor, self.masked_contributors):
            return False
        return contributor.get('id') == claimant_contributor_id

    def _get_verified_count(self, extended_field: dict) -> int:
        count = 0
        if extended_field.get('contributor').get('is_verified'):
            count += 1
        if extended_field.get('is_verified'):
            count += 1
        return count

    def _get_created_at(self, extended_field: dict) -> str:
        return format_date(extended_field['created_at'])

    def _get_updated_at(self, extended_field: dict) -> str:
        return format_date(extended_field['updated_at'])
