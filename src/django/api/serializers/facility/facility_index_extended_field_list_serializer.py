from typing import Union

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

        self.fields: list = ['id', 'is_verified', 'value', 'created_at',
                             'updated_at', 'contributor_name',
                             'contributor_id', 'value_count', 'is_from_claim',
                             'field_name', 'verified_count', 'source_by']
        self.data: list = []

        if exclude_fields:
            for field_name in exclude_fields:
                self.fields.remove(field_name)

        self._serialize_extended_field_list()

    def _serialize_extended_field_list(self) -> None:
        for extended_field in self.extended_field_list:
            serialized_extended_field = {}

            for field in self.fields:
                if field == 'created_at':
                    serialized_extended_field[field] = \
                        self._get_created_at(extended_field)
                elif field == 'updated_at':
                    serialized_extended_field[field] = \
                        self._get_updated_at(extended_field)
                elif field == 'contributor_name':
                    serialized_extended_field[field] = \
                        self._get_contributor_name(extended_field)
                elif field == 'contributor_id':
                    serialized_extended_field[field] = \
                        self._get_contributor_id(extended_field)
                elif field == 'is_from_claim':
                    serialized_extended_field[field] = \
                        self._get_is_from_claim(extended_field)
                elif field == 'verified_count':
                    serialized_extended_field[field] = \
                        self._get_verified_count(extended_field)
                elif field == 'source_by' and self.context.get('source_by', None) is not None:
                    serialized_extended_field[field] = \
                        self.context.get('source_by')
                else:
                    serialized_extended_field[field] = extended_field.get(
                        field)

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
            self._should_display_contributor(extended_field))

    def _get_contributor_id(self, extended_field: dict) -> Union[None, int]:
        embed_mode_active = self.context.get('embed_mode_active')
        if embed_mode_active:
            return None
        return get_contributor_id_from_facilityindex(
            extended_field.get('contributor'),
            self._should_display_contributor(extended_field)
        )

    def _get_is_from_claim(self, extended_field: dict) -> bool:
        return extended_field.get('facility_list_item_id') is None

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
