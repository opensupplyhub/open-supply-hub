class MaskedContributors:
    """
    Value object holding the contributors whose identity must be hidden in a
    paid response, with the matching logic for the different ways a
    contribution is attributed in the ``FacilityIndex`` JSON.

    This is pure data + matching - it never touches the database or the cache.
    ``ContributorMaskingPolicy`` builds it from the cached lookup and hands it
    to the serializers.

    A contribution can be attributed by either the contributor id
    (``contributors``, ``extended_fields``, ``facility_names``,
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

    @classmethod
    def empty(cls):
        """An empty set that never masks anything."""
        return cls()

    def __bool__(self):
        return bool(self.contributor_ids or self.admin_ids or self.names)

    def should_mask(self, contributor):
        """Whether this contributor's identity must be hidden.

        Self-guarding: a falsy ``contributor`` (or an empty set) yields
        ``False``, so callers can apply it unconditionally.
        """
        if not contributor:
            return False
        contributor_id = contributor.get('id')
        if (contributor_id is not None
                and contributor_id in self.contributor_ids):
            return True
        admin_id = contributor.get('admin_id')
        return admin_id is not None and admin_id in self.admin_ids

    def should_mask_name(self, name):
        """Whether a contribution attributed only by name must be hidden.

        Used for ``created_from_info``, whose JSON exposes the contributor
        name but no id.
        """
        return bool(name) and name in self.names
