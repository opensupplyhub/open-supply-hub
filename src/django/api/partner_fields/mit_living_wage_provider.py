from typing import Dict, Any, Optional
from django.contrib.gis.geos import Point
from api.models.us_county_tigerline import USCountyTigerline
from api.partner_fields.base_provider import SystemPartnerFieldProvider


class MITLivingWageProvider(SystemPartnerFieldProvider):
    '''
    Provides wage indicator data based on facility location (geoid).
    Fetches geoid from USCountyTigerline table using facility lat/lng.
    '''

    FIELD_NAME = 'mit_livingwage'
    SYSTEM_CONTRIBUTOR_ID = 6  # TODO: Set to actual system contributor ID.

    def _get_default_contributor_id(self) -> int:
        '''Return the default contributor ID for mit living wage data.'''
        return self.SYSTEM_CONTRIBUTOR_ID

    def _fetch_raw_data(self, facility) -> Optional[USCountyTigerline]:
        '''
        Fetch geoid from database by facility location (lat/lng).
        Returns geoid string if found, None otherwise.
        '''
        if not facility.location:
            return None

        lon = facility.location.x
        lat = facility.location.y

        point = Point(lon, lat, srid=4326)

        point_5070 = point.transform(5070, clone=True)

        try:
            county = USCountyTigerline.objects.filter(
                geometry__contains=point_5070
            ).first()
            
            if county:
                return county
            return None
        except Exception:
            return None

    def _format_data(
        self,
        raw_data: USCountyTigerline,
        contributor_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        '''
        Format mit living wage data into standard partner field structure.
        '''
        raw_values = { "value": raw_data.geoid }

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
            'facility_list_item_id': 1111,  # Random ID for being not from a claim.
            'should_display_association': True,
        }
