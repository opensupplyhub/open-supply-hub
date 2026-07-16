from rest_framework.response import Response
from rest_framework.views import APIView

from ..extended_fields import get_product_types
from ..view_response_cache import cache_view_response


class ProductTypes(APIView):
    throttle_classes = []

    @cache_view_response('product_types')
    def get(self, request):
        """
        Returns a list of suggested product types by combining standard types
        with distinct values submitted by contributors.

        ## Sample Response

            [
                "Accessories",
                "Belts",
                "Caps"
            ]

        """
        return Response(get_product_types())
