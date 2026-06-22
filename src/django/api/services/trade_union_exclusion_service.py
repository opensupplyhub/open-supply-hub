from api.models.contributor.contributor import Contributor
from api.permissions import (
    can_get_union_linked_data,
    should_exclude_union_data,
)


class TradeUnionExclusionService:
    """Resolve which contributor ids must be stripped from a response.

    Centralizes the OSDEV-2786 policy so views do not re-assemble it:

    * the bulk download endpoint strips trade union-contributed fields for
      every caller except members of the ``can_get_union_linked_data`` group;
    * the facility list endpoint strips only for programmatic/non-web-client
      requests, leaving the web client's manual search intact.

    The low-level request predicates live in ``api.permissions`` and the
    actual field removal lives in ``api.trade_union``; this service only
    decides the set of contributor ids to exclude.
    """

    @staticmethod
    def for_list(request):
        """Contributor ids to strip from ``GET /api/facilities/`` responses."""
        if not should_exclude_union_data(request):
            return set()
        return Contributor.objects.union_ids()

    @staticmethod
    def for_download(request):
        """Contributor ids to strip from bulk download responses."""
        if can_get_union_linked_data(request):
            return set()
        return Contributor.objects.union_ids()
