from django.db import migrations, models


ANONYMISE_IN_PAID_PRODUCTS_VERBOSE_NAME = (
    'Anonymise contributor name in paid products'
)
ANONYMISE_IN_PAID_PRODUCTS_HELP_TEXT = (
    "When enabled, this contributor's name is anonymised in "
    'OS Hub paid products - the bulk data download and the '
    'programmatic API - so the data cannot be attributed to '
    'them at scale. Their contributions stay visible on the '
    'public web app and facility profiles.'
)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0218_add_updated_at_to_index_claim_info'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        '''
                        ALTER TABLE api_contributor
                        ADD COLUMN IF NOT EXISTS
                        anonymise_in_paid_products boolean
                        NOT NULL DEFAULT false;
                        ''',
                        '''
                        ALTER TABLE api_historicalcontributor
                        ADD COLUMN IF NOT EXISTS
                        anonymise_in_paid_products boolean
                        NOT NULL DEFAULT false;
                        ''',
                    ],
                    reverse_sql=[
                        '''
                        ALTER TABLE api_historicalcontributor
                        DROP COLUMN IF EXISTS anonymise_in_paid_products;
                        ''',
                        '''
                        ALTER TABLE api_contributor
                        DROP COLUMN IF EXISTS anonymise_in_paid_products;
                        ''',
                    ],
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='contributor',
                    name='anonymise_in_paid_products',
                    field=models.BooleanField(
                        default=False,
                        db_default=False,
                        help_text=ANONYMISE_IN_PAID_PRODUCTS_HELP_TEXT,
                        verbose_name=(
                            ANONYMISE_IN_PAID_PRODUCTS_VERBOSE_NAME
                        ),
                    ),
                ),
                migrations.AddField(
                    model_name='historicalcontributor',
                    name='anonymise_in_paid_products',
                    field=models.BooleanField(
                        default=False,
                        db_default=False,
                        help_text=ANONYMISE_IN_PAID_PRODUCTS_HELP_TEXT,
                        verbose_name=(
                            ANONYMISE_IN_PAID_PRODUCTS_VERBOSE_NAME
                        ),
                    ),
                ),
            ],
        ),
    ]
