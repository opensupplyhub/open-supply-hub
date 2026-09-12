"""Cache key helpers for facilities response visibility."""


def facilities_visibility_token(request):
    """Return a cache key token for the user's response-visibility class.

    The facilities list response varies by user: contributor names are
    anonymized unless the user can view full contributor details, and the
    is_same_contributor flag depends on the user's own contributor. Users
    in the same visibility class receive byte-identical responses and can
    safely share a cache entry.
    """
    user = getattr(request, 'user', None)
    contributor = getattr(user, 'contributor', None)
    contributor_id = getattr(contributor, 'id', None)
    can_view_full = (
        True if user is None or user.is_anonymous
        else user.can_view_full_contrib_details
    )
    detail_level = 'full' if can_view_full else 'limited'
    return f"{contributor_id or 'anon'}:{detail_level}"
