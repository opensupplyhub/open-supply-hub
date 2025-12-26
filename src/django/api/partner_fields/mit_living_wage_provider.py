from typing import Dict, Any, Optional
from django.contrib.gis.geos import Point
from api.models.us_county_tigerline import USCountyTigerline
from api.partner_fields.base_provider import SystemPartnerFieldProvider


class MITLivingWageProvider(SystemPartnerFieldProvider):
    '''
    Provides mit living wage data based on facility location (geoid).
    Fetches geoid from USCountyTigerline table using facility lat/lng.
    '''

    FIELD_NAME = 'mit_living_wage'

    def _get_field_name(self) -> str:
        '''Return the partner field name for this provider.'''
        return self.FIELD_NAME

    def _fetch_raw_data(self, facility) -> Optional[USCountyTigerline]:
        '''
        Fetch geoid from database by facility location (lat/lng).
        Returns geoid string if found, None otherwise.
        Only processes facilities in US, Puerto Rico, or US Virgin Islands.
        '''
        # MIT Living Wage data is only available for US territories
        if facility.country_code not in ['US', 'PR', 'VI']:
            return None

        if not facility.location:
            print(f'No location found for facility {facility.id}')
            return None

        point = Point(
            facility.location.x,
            facility.location.y,
            srid=4326
        )

        point_5070 = point.transform(5070, clone=True)

        try:
            return USCountyTigerline.objects.filter(
                geometry__contains=point_5070
            ).first()
        except Exception as e:
            print(f'Error fetching geoid from database: {e}')
            return None

    def _format_data(
        self,
        raw_data: USCountyTigerline,
        contributor_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        '''
        Format mit living wage data into standard partner field structure.
        '''
        raw_values = {"county_id": raw_data.geoid}

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
