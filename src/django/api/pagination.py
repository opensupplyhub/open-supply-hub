from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework_gis.pagination import GeoJsonPagination


class PageAndSizePagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'pageSize'
    page_size = 50
    max_page_size = 250


class FacilitiesGeoJSONPagination(GeoJsonPagination):
    page_query_param = 'page'
    page_size_query_param = 'pageSize'
    page_size = 50
    max_page_size = 50


class PartnerFieldGroupCursorPagination(CursorPagination):
    """
    Cursor based pagination for partner field groups.
    Allows the client to control the page size via the ?limit= parameter.
    And adds the default ordering by the `order` field.
    """

    page_size = 20
    ordering = ("order", "uuid")
    page_size_query_param = "limit"
    max_page_size = 100
