from django.core.cache import caches

from api.constants import (
    MASKED_CONTRIBUTOR_IDS_CACHE_KEY,
    MASKED_CONTRIBUTOR_IDS_CACHE_TTL_SECONDS,
)
from api.models.contributor.contributor import Contributor
from api.services.masked_contributors import MaskedContributors


class ShouldMaskContribution:
    """
    Resolve which contributors must be masked in OS Hub's paid products - the
    bulk download (``GET /api/facilities-downloads/``) and the programmatic
    facilities API (``GET /api/facilities/``).

    A contribution is masked when ALL of the following hold:

      * the contributor's admin user has the ``anonymise_in_paid_products``
        flag enabled (it defaults to ``False``, so a contributor is only
        anonymised when an OS Hub admin deliberately opts them in), and
      * the request is a programmatic API request, i.e. authenticated with a
        token (``request.auth`` is set). Web-client/manual-search traffic is
        left untouched - the front-end disables the download button for
        anonymised-only searches instead.

    When masked, a contributor's name is relabeled to a neutral
    ``MASKED_CONTRIBUTOR_LABEL`` ("Other"), the contributor id and any list
    metadata are dropped from the response, and none of this touches the
    stored ``Contributor`` record.

    The set of contributors to mask is the same for every paid request, so it
    is cached in the shared ``view_cache`` (memcached) - not the per-process
    ``default`` cache - so every worker sees the same set and a single
    ``view_cache`` flush (see ``Contributor.save``) invalidates it everywhere
    when an admin toggles the flag. The short TTL keeps the lookup cheap while
    letting admin changes propagate without a deploy even if the flush is
    missed.
    """

    @staticmethod
    def _cache():
        # Resolved lazily (not at import time) so test ``override_settings``
        # for ``CACHES`` is honoured.
        return caches['view_cache']

    @staticmethod
    def _load():
        rows = list(
            Contributor.objects
            .filter(anonymise_in_paid_products=True)
            .values_list('id', 'admin_id', 'name')
        )
        contributor_ids = {row[0] for row in rows}
        admin_ids = {row[1] for row in rows if row[1] is not None}
        names = {row[2] for row in rows if row[2]}
        return contributor_ids, admin_ids, names

    @classmethod
    def get_masked_contributors(cls):
        """Return the cached `MaskedContributors` for paid responses."""
        cache = cls._cache()
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
        client and facility profiles keep showing contributor names.
        """
        is_api_user = request is not None and getattr(request, 'auth', None)
        if not is_api_user:
            return MaskedContributors()

        return cls.get_masked_contributors()

    @staticmethod
    def is_masked(contributor, masked):
        """Return True when this contributor's identity must be hidden."""
        return bool(masked) and masked.matches(contributor)
