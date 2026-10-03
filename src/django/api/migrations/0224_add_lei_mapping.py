from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0223_fix_sector_search_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeiMapping',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('os_id', models.CharField(
                    db_index=True,
                    help_text='The OS ID of the facility mapped to the LEI.',
                    max_length=32,
                    unique=True,
                )),
                ('lei', models.CharField(
                    help_text=(
                        'The Legal Entity Identifier mapped to the facility.'
                    ),
                    max_length=20,
                )),
                ('match_type', models.CharField(
                    choices=[
                        ('facility_name', 'facility_name'),
                        ('parent_company', 'parent_company'),
                    ],
                    help_text=(
                        'The facility field on which the GLEIF mapping '
                        'matched.'
                    ),
                    max_length=14,
                )),
                ('matched_name', models.TextField(
                    blank=True,
                    default='',
                    help_text=(
                        'The legal entity name against which the mapping '
                        'matched.'
                    ),
                )),
                ('score', models.FloatField(
                    blank=True,
                    help_text=(
                        'The match score reported by the mapping process.'
                    ),
                    null=True,
                )),
                ('mapping_file_date', models.DateField(
                    blank=True,
                    help_text=(
                        'The date of the GLEIF mapping file with this '
                        'mapping, when provided.'
                    ),
                    null=True,
                )),
                ('status', models.CharField(
                    choices=[
                        ('active', 'active'),
                        ('removed', 'removed'),
                        ('denylisted', 'denylisted'),
                    ],
                    default='active',
                    help_text=(
                        'The lifecycle status of the mapping. An active '
                        'mapping is materialized as an extended field. A '
                        'removed mapping was absent from the most recent '
                        'mapping file. A denylisted mapping is never '
                        'recreated by ingestion.'
                    ),
                    max_length=11,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
