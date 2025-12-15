from typing import Dict, Any, Optional
from django.core.exceptions import ObjectDoesNotExist
from api.models.wage_indicator_country_data import WageIndicatorCountryData
from api.partner_fields.base_provider import SystemPartnerFieldProvider


class WageIndicatorProvider(SystemPartnerFieldProvider):
    '''
    Provides wage indicator data based on facility country code.
    Fetches data from WageIndicatorCountryData table.
    '''

    FIELD_NAME = 'wage_indicator'
    SYSTEM_CONTRIBUTOR_ID = 7783  # TODO: Set to actual system contributor ID.

    def get_field_name(self) -> str:
        '''Return the field name this provider handles.'''
        return self.FIELD_NAME

    def _get_default_contributor_id(self) -> int:
        '''Return the default contributor ID for wage indicator data.'''
        return self.SYSTEM_CONTRIBUTOR_ID

    def _fetch_raw_data(self, facility) -> Optional[WageIndicatorCountryData]:
        '''Fetch wage indicator data from database by country code.'''
        try:
            return WageIndicatorCountryData.objects.get(
                country_code=facility.country_code
            )
        except ObjectDoesNotExist:
            return None

    def _format_data(
        self,
        raw_data: WageIndicatorCountryData,
        contributor_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        '''Format wage indicator data into standard partner field structure.'''
        return {
            'id': None,
            'value': {
                'raw_values': {
                    'living_wage_link_national': (
                        raw_data.living_wage_link_national
                    ),
                    'minimum_wage_link_english': (
                        raw_data.minimum_wage_link_english
                    ),
                    'minimum_wage_link_national': (
                        raw_data.minimum_wage_link_national
                    ),
                }
            },
            'created_at': raw_data.created_at.isoformat(),
            'updated_at': raw_data.updated_at.isoformat(),
            'field_name': self.FIELD_NAME,
            'contributor': contributor_info,
            'is_verified': False,
            'value_count': 0,
            'facility_list_item_id': 1111,  # Random ID for being not from a claim.
            'should_display_association': True,
        }
