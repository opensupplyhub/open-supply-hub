from django.db import connection, models, transaction
from django.db.models.functions import Lower
from simple_history.models import HistoricalRecords

from api.helpers.claim_profile_options import rename_claim_option_value


class ClaimProfileOptionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def active_names(self):
        return list(self.active().values_list('name', flat=True))


class ClaimProfileOption(models.Model):
    """
    One selectable value in a claim-profile dropdown (affiliations or
    certifications/standards/regulations), managed in the Django admin.

    `FacilityClaim` stores the chosen values as plain strings, so the
    option's `name` is exactly what lands on the claim, in OpenSearch,
    in the API and in downloads. Consequences:

    - Renaming an option rewrites every claim holding the old name (see
      `save` and `api.helpers.claim_profile_options`).
    - Options are never deleted, only deactivated: an inactive option
      is no longer offered for new claims, but the claims that already
      hold it keep it.
    """

    # The FacilityClaim array field this option's values are stored in.
    claim_field = None

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=(
            'The name shown in the claim form and stored on claims. '
            'Renaming it also updates every existing claim that holds the '
            'old name. 50 characters at most.'
        ),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=(
            'Whether the claim form offers this option. Untick it to stop '
            'offering an option without touching the claims that already '
            'hold it.'
        ),
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text=(
            'Position in the dropdown; lower numbers come first. Options '
            'with the same number are sorted by name.'
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords(inherit=True)

    objects = ClaimProfileOptionQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ('sort_order', 'name')
        constraints = [
            # "cascale" next to "Cascale" would be two options for one
            # organization; a case-only rename of one row is still fine.
            models.UniqueConstraint(
                Lower('name'),
                name='%(app_label)s_%(class)s_name_ci_unique',
                violation_error_message=(
                    'An option with this name already exists '
                    '(names are compared ignoring case).'
                ),
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.name:
            self.name = self.name.strip()

    def save(self, *args, **kwargs):
        """
        Save the option and, if its name changed, rewrite the claims that
        hold the old name, all in one transaction.

        The number of rewritten claims is left on
        `self.renamed_claims_count` so the admin can report it.
        """
        self.renamed_claims_count = 0
        with transaction.atomic():
            previous_name = None
            if self.pk is not None:
                previous_name = (
                    type(self).objects
                    .filter(pk=self.pk)
                    .values_list('name', flat=True)
                    .first()
                )
            super().save(*args, **kwargs)
            if previous_name is not None and previous_name != self.name:
                self.renamed_claims_count = rename_claim_option_value(
                    connection,
                    self.claim_field,
                    previous_name,
                    self.name,
                )


class ClaimAffiliation(ClaimProfileOption):
    claim_field = 'facility_affiliations'

    class Meta(ClaimProfileOption.Meta):
        verbose_name = 'claim affiliation'
        verbose_name_plural = 'claim affiliations'


class ClaimCertification(ClaimProfileOption):
    claim_field = 'facility_certifications'

    class Meta(ClaimProfileOption.Meta):
        verbose_name = 'claim certification/standard/regulation'
        verbose_name_plural = 'claim certifications/standards/regulations'
