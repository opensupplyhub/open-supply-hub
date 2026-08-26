from django.db import migrations, models


NOTE_TYPE_HELP_TEXT = (
    'Whether the note is internal to moderators or was emailed to the '
    'claimant. Rows created before this field existed default to INTERNAL '
    'regardless of how they were delivered.'
)

NOTE_TYPE_CHOICES = [
    ('INTERNAL', 'INTERNAL'),
    ('CLAIMANT_MESSAGE', 'CLAIMANT_MESSAGE'),
]


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0233_index_facility_processing_search'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        '''
                        ALTER TABLE api_facilityclaimreviewnote
                        ADD COLUMN IF NOT EXISTS
                        note_type varchar(200)
                        NOT NULL DEFAULT 'INTERNAL';
                        ''',
                        '''
                        ALTER TABLE api_historicalfacilityclaimreviewnote
                        ADD COLUMN IF NOT EXISTS
                        note_type varchar(200)
                        NOT NULL DEFAULT 'INTERNAL';
                        ''',
                    ],
                    reverse_sql=[
                        '''
                        ALTER TABLE api_historicalfacilityclaimreviewnote
                        DROP COLUMN IF EXISTS note_type;
                        ''',
                        '''
                        ALTER TABLE api_facilityclaimreviewnote
                        DROP COLUMN IF EXISTS note_type;
                        ''',
                    ],
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='facilityclaimreviewnote',
                    name='note_type',
                    field=models.CharField(
                        max_length=200,
                        choices=NOTE_TYPE_CHOICES,
                        default='INTERNAL',
                        db_default='INTERNAL',
                        help_text=NOTE_TYPE_HELP_TEXT,
                    ),
                ),
                migrations.AddField(
                    model_name='historicalfacilityclaimreviewnote',
                    name='note_type',
                    field=models.CharField(
                        max_length=200,
                        choices=NOTE_TYPE_CHOICES,
                        default='INTERNAL',
                        db_default='INTERNAL',
                        help_text=NOTE_TYPE_HELP_TEXT,
                    ),
                ),
            ],
        ),
    ]
