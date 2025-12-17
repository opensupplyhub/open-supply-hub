from typing import Dict, Any, Optional
import logging

from api.models.wage_indicator_country_data import WageIndicatorCountryData
from api.partner_fields.base_provider import SystemPartnerFieldProvider
from api.models.partner_field import PartnerField

logger = logging.getLogger(__name__)


class WageIndicatorProvider(SystemPartnerFieldProvider):
    '''
    Provides wage indicator data based on facility country code.
    Fetches data from WageIndicatorCountryData table.
    '''

    FIELD_NAME = 'wage_indicator'

    def _get_default_contributor_id(self) -> int:
        '''
        Return the default contributor ID for wage indicator data.
        Gets the first contributor assigned to the wage_indicator
        partner field.
        '''
        partner_field = PartnerField.objects \
            .get_all_including_inactive() \
            .get(name=self.FIELD_NAME)
        # By default, it is assumed that there is only one contributor assigned
        # to the wage_indicator partner field.
        contributor = partner_field.contributor_set.first()
        if contributor:
            return contributor.id

        logger.error(
            f'No contributor found for {self.FIELD_NAME} partner field. '
            'However, the contributor must be assigned to this partner field '
            'since it is a system field.'
        )
        # Silently return None if no contributor is found.
        return None

    def _fetch_raw_data(self, facility) -> Optional[WageIndicatorCountryData]:
        '''Fetch wage indicator data from database by country code.'''
        try:
            return WageIndicatorCountryData.objects.get(
                country_code=facility.country_code
            )
        except WageIndicatorCountryData.DoesNotExist:
            return None

    def _format_data(
        self,
        raw_data: WageIndicatorCountryData,
        contributor_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        '''
        Format wage indicator data into standard partner field structure.
        '''
        # Get links with their configured display text.
        links_with_text = raw_data.get_links_with_text()

        # Build raw_values dict with link URLs and their display text.
        raw_values = {}
        for link in links_with_text:
            link_type = link['type']
            raw_values[link_type] = link['url']
            raw_values[f'{link_type}_text'] = link['text']

        return {
            'id': None,
            'value': {
                'raw_values': raw_values,
            },
            'created_at': raw_data.created_at.isoformat(),
            'updated_at': raw_data.updated_at.isoformat(),
            'field_name': self.FIELD_NAME,
            'contributor': contributor_info,
            'is_verified': False,
            'value_count': 1,
            # Random ID for being not from a claim.
            'facility_list_item_id': 1111,
            'should_display_association': True,
        }
