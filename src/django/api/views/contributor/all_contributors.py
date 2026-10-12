from rest_framework.response import Response
from rest_framework.views import APIView

from ...view_response_cache import cache_view_response
from .active_contributors import active_contributors


class AllContributors(APIView):
    throttle_classes = []

    @cache_view_response('all_contributors')
    def get(self, request):
        """
        Returns list contributors as a list of tuples of
        contributor IDs, names and types.

        ## Sample Response

            [
                [1, "Contributor One", "Brand/Retailer"]
                [2, "Contributor Two", "Service Provider"]
            ]
        """
        response_data = [
            (
                contributor.id,
                contributor.name,
                contributor.other_contrib_type
                if contributor.contrib_type == "Other"
                else contributor.contrib_type
            )
            for contributor in active_contributors().order_by('name')
        ]

        return Response(response_data)
