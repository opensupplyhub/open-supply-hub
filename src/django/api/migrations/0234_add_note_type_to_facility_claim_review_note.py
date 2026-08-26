from django.db import migrations, models


NOTE_TYPE_HELP_TEXT = (
    'How the note was delivered. CLAIMANT_MESSAGE = emailed to the '
    'claimant via the message-claimant action. INTERNAL = not sent '
    'directly, although the reason text in deny/revoke notes may still '
    'reach the claimant inside status emails. Rows created before this '
    'field existed default to INTERNAL regardless of delivery.'
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
