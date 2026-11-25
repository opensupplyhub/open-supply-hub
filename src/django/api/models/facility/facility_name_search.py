from django.db.models import Lookup, TextField, Transform
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


class StrictWordSimilarLookup(Lookup):
    """
    Postgres ``strict_word_similarity`` via its indexed ``<<%`` operator.

    Used after the ``immutable_unaccent`` transform, this emits exactly
    the expression the OSDEV-3793 trigram index is built on, so a fuzzy
    probe is a Bitmap Index Scan rather than a table read (149 ms over
    2.5M rows, measured). The operator applies the database default
    ``pg_trgm.strict_word_similarity_threshold`` (0.5), which catches the
    reported one-letter typos: strict_word_similarity('TEXOPORT',
    'TEXPORT') = 0.545. See OSDEV-3906.
    """

    lookup_name = 'strict_word_similar'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        # The search term is folded the same way as the column, as the
        # bilateral transform does for icontains.
        sql = (
            'UPPER(public.immutable_unaccent({rhs})) <<%% UPPER({lhs})'
        ).format(rhs=rhs, lhs=lhs)
        return sql, rhs_params + lhs_params


TextField.register_lookup(StrictWordSimilarLookup)
