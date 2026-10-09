import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q

FACILITY_HELP_TEXT = (
    'The facility now associated with the os_id. NULL when the OS ID was '
    'retired (reason NOT_A_FACILITY) and redirects nowhere.'
)
REASON_CHOICES = [
    ('MERGE', 'MERGE'),
    ('DELETE', 'DELETE'),
    ('NOT_A_FACILITY', 'NOT_A_FACILITY'),
]
RETIRED_SOURCE_HELP_TEXT = (
    'For a NOT_A_FACILITY tombstone, the detection source of the retired '
    'candidate (copied from Facility.source), so ingest can suppress '
    're-creation.'
)
RETIRED_EXTERNAL_ID_HELP_TEXT = (
    'For a NOT_A_FACILITY tombstone, the identifier of the retired '
    'candidate in its detection source (copied from Facility.external_id).'
)
RETIREMENT_TALLY_HELP_TEXT = (
    'For a NOT_A_FACILITY tombstone, the final community vote tally that '
    'retired the candidate, e.g. {"confirmed": 1, "not_a_facility": 5, '
    '"retired_at": "<ISO 8601>", "retired_by": <user id>}.'
)


def tombstone_fields():
    return [
        (
            'retired_source',
            models.CharField(
                blank=True,
                help_text=RETIRED_SOURCE_HELP_TEXT,
                max_length=200,
                null=True,
            ),
        ),
        (
            'retired_external_id',
            models.CharField(
                blank=True,
                help_text=RETIRED_EXTERNAL_ID_HELP_TEXT,
                max_length=200,
                null=True,
            ),
        ),
        (
            'retirement_tally',
            models.JSONField(
                blank=True,
                help_text=RETIREMENT_TALLY_HELP_TEXT,
                null=True,
            ),
        ),
    ]


class Migration(migrations.Migration):
    """
    Let a FacilityAlias be a terminal NOT_A_FACILITY tombstone instead of a
    redirect (OSDEV-3246): nullable facility, a wider reason column for the
    new choice, the retired detection key and vote tally, and a partial
    index on (retired_source, retired_external_id) for the ingest check.

    api_facilityalias is a small table (one row per merged or deleted
    facility), so plain Django operations are used. Most of the DDL is
    metadata-only on Postgres (DROP NOT NULL, widening varchar, adding
    nullable columns, a partial index that starts empty), but making the
    facility FK nullable is not: Django emits DROP CONSTRAINT, DROP NOT
    NULL and then re-adds the FOREIGN KEY constraint, which validates
    every existing facility_id against api_facility and so takes a brief
    SHARE ROW EXCLUSIVE lock on api_facility as well as the ACCESS
    EXCLUSIVE lock on api_facilityalias. All of it runs inside one
    transaction under the lock_timeout below; SET LOCAL lasts until that
    transaction ends, so it also covers any constraint or index statement
    Django leaves until after the last operation. The
    long-running logstash sync SELECT reads api_facilityalias, so without
    the timeout the ALTERs would queue behind it with every other reader
    queueing behind them; with it the migration fails fast, rolls back
    completely and rerunning migrate is the whole recovery.

    Reversing is only possible while no tombstone exists. The reverse
    puts NOT NULL back on api_facilityalias.facility_id and narrows
    reason to varchar(6) on both api_facilityalias and
    api_historicalfacilityalias, and a NOT_A_FACILITY row (facility_id
    NULL, 14-character reason, plus the history row django-simple-history
    wrote for it) violates both. Decide whether discarding the retirement
    records is acceptable, then clean both tables before migrating back:

        DELETE FROM api_historicalfacilityalias
            WHERE reason = 'NOT_A_FACILITY';
        DELETE FROM api_facilityalias
            WHERE reason = 'NOT_A_FACILITY';
    """

    dependencies = [
        ('api', '0245_add_claim_quality_check_switch'),
    ]

    operations = [
        # SET LOCAL lasts until the migration transaction ends, so it also
        # covers any ADD CONSTRAINT / CREATE INDEX statement Django leaves
        # until after the last operation. The mirror-image RunSQL at the
        # end makes the same true when migrating backwards.
        migrations.RunSQL(
            sql="SET LOCAL lock_timeout = '5s';",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='facilityalias',
            name='facility',
            field=models.ForeignKey(
                blank=True,
                help_text=FACILITY_HELP_TEXT,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to='api.facility',
            ),
        ),
        migrations.AlterField(
            model_name='historicalfacilityalias',
            name='facility',
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text=FACILITY_HELP_TEXT,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name='+',
                to='api.facility',
            ),
        ),
        migrations.AlterField(
            model_name='facilityalias',
            name='reason',
            field=models.CharField(
                choices=REASON_CHOICES,
                help_text='The reason why this alias was created',
                max_length=14,
            ),
        ),
        migrations.AlterField(
            model_name='historicalfacilityalias',
            name='reason',
            field=models.CharField(
                choices=REASON_CHOICES,
                help_text='The reason why this alias was created',
                max_length=14,
            ),
        ),
        *[
            migrations.AddField(
                model_name=model_name,
                name=name,
                field=field,
            )
            for model_name in ('facilityalias', 'historicalfacilityalias')
            for name, field in tombstone_fields()
        ],
        migrations.AddIndex(
            model_name='facilityalias',
            index=models.Index(
                condition=Q(retired_external_id__isnull=False),
                fields=['retired_source', 'retired_external_id'],
                name='api_facilityalias_retired_idx',
            ),
        ),
        migrations.RunSQL(
            sql=migrations.RunSQL.noop,
            reverse_sql="SET LOCAL lock_timeout = '5s';",
        ),
    ]
