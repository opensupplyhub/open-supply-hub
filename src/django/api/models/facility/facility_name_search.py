from django.db.models import TextField, Transform
from django.db.models.fields import CharField


class ImmutableUnaccentTransform(Transform):
    """
    Accent-folding that an expression index can be built on.

    Django's own ``__unaccent`` emits ``unaccent()``, which is ``STABLE``
    rather than ``IMMUTABLE`` because it reads a reloadable dictionary, so
    Postgres refuses to index it and every free-text search falls back to a
    sequential scan. See OSDEV-3793.
    """

    lookup_name = 'immutable_unaccent'
    function = 'public.immutable_unaccent'
    output_field = TextField()
    # As Django's own Unaccent: fold the search term as well as the column,
    # or an accented query stops matching its unaccented spelling.
    bilateral = True


CharField.register_lookup(ImmutableUnaccentTransform)
TextField.register_lookup(ImmutableUnaccentTransform)
