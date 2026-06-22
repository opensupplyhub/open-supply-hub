from django.db.models import (
  BooleanField,
  Count,
  ExpressionWrapper,
  Q,
  QuerySet,
)


class ContributorManager(QuerySet):

    # TODO: Will revisit trigram thresholds.
    # Temporary change to iexact to fix Ralph Lauren upload issue
    def filter_by_name(self, name):
        """
        Perform an exact match on contributor names
        """
        return (
            self
            .order_by_active_and_verified()
            .filter(name__iexact=name)
        )

    def order_by_active_and_verified(self):
        return (
            self
            .annotate(
                active_source_count=Count(
                    Q(source__is_active=True))
                )
            .annotate(
                has_active_sources=ExpressionWrapper(
                    Q(active_source_count__gt=0),
                    BooleanField())
                )
            .order_by('-is_verified', '-has_active_sources', '-created_at')
        )

    def unions(self):
        """Restrict the queryset to trade union contributors."""
        return self.filter(contrib_type=self.model.UNION_CONTRIB_TYPE)

    def union_ids(self):
        """Return the set of trade union contributor ids (OSDEV-2786)."""
        return set(self.unions().values_list('id', flat=True))
