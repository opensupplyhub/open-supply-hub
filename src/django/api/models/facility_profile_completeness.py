from django.db import models

from api.profile_completeness import ClassifierTiers, level_for_score


def _choices(values):
    return [(value, value) for value in values]


class FacilityProfileCompleteness(models.Model):
    '''
    One run's profile completeness reading for a production location: the
    numeric score with its components, and/or the model-backed
    classification of the same profile. Both are computed outside this
    application and loaded with the load_profile_completeness command.

    Rows are kept per run date rather than overwritten, so the score and
    the classification can be compared with each other and across runs.
    '''

    facility = models.ForeignKey(
        'Facility',
        on_delete=models.CASCADE,
        related_name='profile_completeness_runs',
    )
    run_date = models.DateField(
        help_text='The date the score and/or classification was computed.',
    )

    score = models.FloatField(
        null=True,
        blank=True,
        help_text='Profile completeness score from 0 to 1.',
    )
    components = models.JSONField(
        default=dict,
        blank=True,
        help_text='The scorer components the score averages, each 0 to 1.',
    )
    scorer_version = models.CharField(max_length=50, blank=True)

    classifier_tier = models.CharField(
        max_length=10,
        blank=True,
        choices=_choices(ClassifierTiers.FINAL),
        help_text='Final tier from the model-backed classification.',
    )
    classifier_agreement_tier = models.CharField(
        max_length=10,
        blank=True,
        choices=_choices(ClassifierTiers.AGREEMENT),
        help_text='Contributor agreement check of the classification.',
    )
    classifier_field_tier = models.CharField(
        max_length=10,
        blank=True,
        choices=_choices(ClassifierTiers.FINAL),
        help_text='Field data check of the classification.',
    )
    classifier_model = models.CharField(
        max_length=100,
        blank=True,
        help_text='Name and version of the model that classified it.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'profile completeness run'
        verbose_name_plural = 'profile completeness runs'
        unique_together = ('facility', 'run_date')
        ordering = ('-run_date',)

    @property
    def level(self):
        return level_for_score(self.score)

    @property
    def classifier_level(self):
        return ClassifierTiers.LEVELS.get(self.classifier_tier)

    def __str__(self):
        return f'{self.facility_id} on {self.run_date}'
