from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.viewsets import ViewSet

from api.models.country_stats import CountryStats
from api.models.partner_field import PartnerField


# The rollup is rebuilt once a day, so a shared cache for an hour costs
# nothing in freshness and keeps the map off the database entirely. The
# response is identical for every caller, which is the whole advantage
# over the vector tiles this replaces: those varied per filter and so
# could never really be cached.
CACHE_SECONDS = 60 * 60


class CountryStatsViewSet(ViewSet):
    '''
    Precomputed per-country figures behind the country map.

    `list` returns every country with its location count and nothing else:
    that is the payload that draws the whole map, and it is a few kilobytes.
    `retrieve` returns one country's sector breakdown and the Spotlight
    partner fields holding data for it, fetched only when someone clicks.
    '''

    lookup_field = 'country_code'

    @method_decorator(cache_control(max_age=CACHE_SECONDS, public=True))
    def list(self, request):
        rows = CountryStats.objects.values_list(
            'country_code', 'location_count', 'computed_at'
        )

        countries = [
            {'country_code': country_code, 'location_count': location_count}
            for country_code, location_count, _ in rows
        ]

        return Response({
            'count': len(countries),
            # Surfaced so a stalled rebuild is visible to callers rather
            # than silently serving numbers that look current.
            'computed_at': rows[0][2] if rows else None,
            'countries': countries,
        })

    @method_decorator(cache_control(max_age=CACHE_SECONDS, public=True))
    def retrieve(self, request, country_code=None):
        row = CountryStats.objects.filter(
            country_code=(country_code or '').upper()
        ).first()

        if row is None:
            # A country with no open production locations has no row, which
            # is a legitimate answer rather than an error on our side. Say
            # so explicitly instead of returning an empty object that reads
            # like a glitch.
            return Response(
                {
                    'detail': (
                        'No production locations recorded for this country.'
                    )
                },
                status=HTTP_404_NOT_FOUND,
            )

        return Response({
            'country_code': row.country_code,
            'location_count': row.location_count,
            'sectors': row.sectors,
            'partner_fields': self.__labelled(row.partner_fields),
            'computed_at': row.computed_at,
        })

    @staticmethod
    def __labelled(field_names):
        '''
        The rollup stores partner field names, which are snake_case and not
        meant for reading. Resolve them to the labels the admin maintains so
        callers do not have to keep their own copy of that mapping.

        A field with no label set falls back to a readable form of its name
        rather than showing the raw value.
        '''
        labels = dict(
            PartnerField.objects
            .filter(name__in=field_names)
            .values_list('name', 'label')
        )

        return [
            {
                'name': name,
                'label': labels.get(name) or name.replace('_', ' ').title(),
            }
            for name in field_names
        ]
