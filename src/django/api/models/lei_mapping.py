from django.db import models


class LeiMapping(models.Model):
    """
    Ledger of GLEIF OS Hub-to-LEI mappings ingested by the ingest_lei_mappings
    management command. Holds one current row per OS ID and tracks the
    lifecycle of the mapping across ingestion runs.
    """
    FACILITY_NAME = 'facility_name'
    PARENT_COMPANY = 'parent_company'

    MATCH_TYPE_CHOICES = (
        (FACILITY_NAME, FACILITY_NAME),
        (PARENT_COMPANY, PARENT_COMPANY),
    )

    ACTIVE = 'active'
    REMOVED = 'removed'
    BLACKLISTED = 'blacklisted'

    STATUS_CHOICES = (
        (ACTIVE, ACTIVE),
        (REMOVED, REMOVED),
        (BLACKLISTED, BLACKLISTED),
    )

    os_id = models.CharField(
        max_length=32,
        null=False,
        blank=False,
        unique=True,
        db_index=True,
        help_text='The OS ID of the facility mapped to the LEI.')
    lei = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        help_text='The Legal Entity Identifier mapped to the facility.')
    match_type = models.CharField(
        max_length=14,
        null=False,
        blank=False,
        choices=MATCH_TYPE_CHOICES,
        help_text='The facility field on which the GLEIF mapping matched.')
    matched_name = models.TextField(
        null=False,
        blank=True,
        default='',
        help_text='The legal entity name against which the mapping matched.')
    score = models.FloatField(
        null=True,
        blank=True,
        help_text='The match score reported by the mapping process.')
    mapping_file_date = models.DateField(
        null=False,
        help_text='The date of the GLEIF mapping file with this mapping.')
    status = models.CharField(
        max_length=11,
        null=False,
        blank=False,
        choices=STATUS_CHOICES,
        default=ACTIVE,
        help_text=('The lifecycle status of the mapping. An active mapping '
                   'is materialized as an extended field. A removed mapping '
                   'was absent from the most recent mapping file. A '
                   'blacklisted mapping is never recreated by ingestion.'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.os_id} -> {self.lei} ({self.status})'
