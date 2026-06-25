from django.core.cache import cache

from api.constants import (
    MASKED_CONTRIBUTOR_IDS_CACHE_KEY,
    MASKED_CONTRIBUTOR_IDS_CACHE_TTL_SECONDS,
)
from api.models.contributor.contributor import Contributor


class MaskedContributors:
    """
    The contributors whose identity must be hidden in a paid response.

    A contribution can be attributed in the FacilityIndex JSON by either the
    contributor id (``contributors``, ``extended_fields``, ``facility_names``,
    ``facility_addresses``, ``item_sectors``, ``claim_info``) or only by the
    admin/user id (``facility_locations``, ``facility_list_items``), so we keep
    both sets and match on whichever key a given contributor blob carries.

    The ``created_from_info`` JSON carries neither id, so masked contributor
    names are also kept and matched by name there. The name set is built from
    the same query, so it still honours the per-contributor flag.
    """

    __slots__ = ('contributor_ids', 'admin_ids', 'names')

    def __init__(self, contributor_ids=None, admin_ids=None, names=None):
        self.contributor_ids = set(contributor_ids or ())
        self.admin_ids = set(admin_ids or ())
        self.names = set(names or ())

    def __bool__(self):
        return bool(self.contributor_ids or self.admin_ids or self.names)

    def matches(self, contributor):
        if not contributor:
            return False
        contributor_id = contributor.get('id')
        if (contributor_id is not None
                and contributor_id in self.contributor_ids):
            return True
        admin_id = contributor.get('admin_id')
        return admin_id is not None and admin_id in self.admin_ids

    def masks_name(self, name):
        """Match a contribution that is only attributed by name.

        Used for ``created_from_info``, whose JSON exposes the contributor
        name but no id.
        """
        return bool(name) and name in self.names


class ShouldMaskContribution:
    """
    Resolve which contributors must be masked in OS Hub's paid products - the
    bulk download (``GET /api/facilities-downloads/``) and the programmatic
    facilities API (``GET /api/facilities/``).

    A contribution is masked when ALL of the following hold:

      * the contributor is a trade union (``contrib_type == 'Union'``), and
      * the contributor's admin user has the ``hide_in_paid_products`` flag
        enabled (it defaults to ``True``, so unions are protected unless an
        OS Hub admin deliberately opts them back in), and
      * the request is a programmatic API request, i.e. authenticated with a
        token (``request.auth`` is set). Web-client/manual-search traffic is
        left untouched - the front-end disables the download button for union
        searches instead.

    When masked, a contributor's name is relabeled to a neutral
    ``MASKED_CONTRIBUTOR_LABEL`` ("Other"), the contributor id and any list
    metadata are dropped from the response, and none of this touches the
    stored ``Contributor`` record.

    The set of contributors to mask is the same for every paid request, so it
    is cached (mirroring ``get_cached_all_partner_fields``) and shared across
    every endpoint that builds a paid response. The short TTL keeps the lookup
    cheap while letting admin changes propagate without a deploy.
    """

    @staticmethod
    def _load():
        rows = (
            Contributor.objects
            .filter(
                contrib_type=Contributor.UNION_CONTRIB_TYPE,
                admin__hide_in_paid_products=True,
            )
            .values_list('id', 'admin_id', 'name')
        )
        contributor_ids = {row[0] for row in rows}
        admin_ids = {row[1] for row in rows if row[1] is not None}
        names = {row[2] for row in rows if row[2]}
        return contributor_ids, admin_ids, names

    @classmethod
    def get_masked_contributors(cls):
        """Return the cached `MaskedContributors` for paid responses."""
        cached = cache.get(MASKED_CONTRIBUTOR_IDS_CACHE_KEY)
        if cached is None:
            cached = cls._load()
            cache.set(
                MASKED_CONTRIBUTOR_IDS_CACHE_KEY,
                cached,
                MASKED_CONTRIBUTOR_IDS_CACHE_TTL_SECONDS,
            )
        contributor_ids, admin_ids, names = cached
        return MaskedContributors(contributor_ids, admin_ids, names)

    @classmethod
    def for_request(cls, request):
        """
        Return the `MaskedContributors` to hide for this request.

        Empty for everything that is not a programmatic API call, so the web
        client and facility profiles keep showing union contributor names.
        """
        is_api_user = request is not None and getattr(request, 'auth', None)
        if not is_api_user:
            return MaskedContributors()

        return cls.get_masked_contributors()

    @staticmethod
    def is_masked(contributor, masked):
        """Return True when this contributor's identity must be hidden."""
        return bool(masked) and masked.matches(contributor)
