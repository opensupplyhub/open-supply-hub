from api.constants import (MASKED_CONTRIBUTOR_IDS_CACHE_KEY,
                           MASKED_CONTRIBUTOR_IDS_CACHE_TTL_SECONDS)
from api.models.contributor.contributor import Contributor
from api.services.masked_contributors import MaskedContributors

from django.core.cache import caches


class ContributorMaskingPolicy:
    """
    Decides which contributors to anonymise on OS Hub's *paid* surfaces and
    returns a ready-to-apply :class:`MaskedContributors` set.

    The flagged set is identical for every paid request, so it is cached in the
    shared ``view_cache`` (memcached, not the per-process ``default`` cache) so
    every worker sees the same set; a single key delete (see
    ``Contributor.save``) invalidates it everywhere when an admin toggles the
    flag. The short TTL keeps the lookup cheap while letting changes propagate
    without a deploy even if the delete is missed.
    """

    @classmethod
    def for_download(cls):
        """``GET /api/facilities-downloads/`` - always masked."""
        return cls.flagged_contributors()

    @classmethod
    def for_facilities_api(cls, request, flagged=None):
        """``GET /api/facilities/`` and ``/{id}/`` - masked only for token
        (programmatic) API callers; empty for web / manual-search traffic.

        Pass ``flagged`` when the caller already resolved the full set (the
        list view does, for ``anonymised_only``) to avoid a second cache read.
        """
        if not cls._is_token_api_request(request):
            return MaskedContributors.empty()
        return flagged if flagged is not None else cls.flagged_contributors()

    @classmethod
    def flagged_contributors(cls):
        """The full set of contributors flagged ``anonymise_in_paid_products``
        (cached). Endpoint-agnostic; also drives the ``anonymised_only`` flag.
        """
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

    @staticmethod
    def _is_token_api_request(request):
        """A programmatic API call is authenticated with a token."""
        return request is not None and bool(getattr(request, 'auth', None))

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
