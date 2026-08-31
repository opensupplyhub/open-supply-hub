import django.db.models.deletion
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import connection, migrations, models
from django.db.migrations import RunPython

from api.migrations._isic_taxonomy_helper import (
    clear_isic_taxonomy_config,
    seed_isic_taxonomy_config,
)
from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def add_isic_indexing_functions(apps, schema_editor):
    helper.run_sql_files([
        '0234_extract_isic_code.sql',
        '0234_index_isic_4.sql',
    ])


def revert_isic_indexing_functions(apps, schema_editor):
    helper.run_sql_files([
        '0234_revert_index_isic_4.sql',
    ])


def update_indexing_procedures(apps, schema_editor):
    helper.run_sql_files([
        '0234_index_facilities.sql',
        '0234_index_facilities_by.sql',
    ])


def revert_indexing_procedures(apps, schema_editor):
    helper.run_sql_files([
        '0171_index_facilities.sql',
        '0171_index_facilities_by.sql',
    ])


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0233_index_facility_processing_search'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilityindex',
            name='isic_class',
            field=ArrayField(
                base_field=models.CharField(
                    db_index=True,
                    help_text=(
                        'Normalized ISIC Rev 4 class codes from isic_4 '
                        'ExtendedField.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='isic_division',
            field=ArrayField(
                base_field=models.CharField(
                    db_index=True,
                    help_text=(
                        'Normalized ISIC Rev 4 division codes from isic_4 '
                        'ExtendedField.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='isic_group',
            field=ArrayField(
                base_field=models.CharField(
                    db_index=True,
                    help_text=(
                        'Normalized ISIC Rev 4 group codes from isic_4 '
                        'ExtendedField.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name='facilityindex',
            name='isic_section',
            field=ArrayField(
                base_field=models.CharField(
                    db_index=True,
                    help_text=(
                        'Normalized ISIC Rev 4 section codes from isic_4 '
                        'ExtendedField.'
                    ),
                    max_length=10,
                ),
                default=list,
                size=None,
            ),
        ),
        RunPython(add_isic_indexing_functions, revert_isic_indexing_functions),
        RunPython(update_indexing_procedures, revert_indexing_procedures),
        migrations.CreateModel(
            name='IsicTaxonomyConfig',
            fields=[
                (
                    'id',
                    models.PositiveSmallIntegerField(
                        default=1,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    'is_active',
                    models.BooleanField(
                        default=False,
                        help_text=(
                            'When enabled, the ISIC Rev 4 filter is shown in '
                            'extended search.'
                        ),
                    ),
                ),
                (
                    'version',
                    models.PositiveIntegerField(
                        default=0,
                        help_text=(
                            'Monotonic publish version; used in the S3 key '
                            'prefix.'
                        ),
                    ),
                ),
                (
                    'source_file',
                    models.FileField(
                        blank=True,
                        help_text=(
                            'Most recently uploaded taxonomy spreadsheet.'
                        ),
                        null=True,
                        upload_to='taxonomy/isic4/source/',
                    ),
                ),
                (
                    'source_filename',
                    models.CharField(
                        blank=True,
                        default='',
                        help_text=(
                            'Original filename from the admin upload, for '
                            'display only.'
                        ),
                        max_length=255,
                    ),
                ),
                (
                    'json_s3_key',
                    models.CharField(
                        blank=True,
                        default='',
                        help_text=(
                            'S3 key for the published isic_rev4.json artifact.'
                        ),
                        max_length=512,
                    ),
                ),
                (
                    'bundle_s3_key',
                    models.CharField(
                        blank=True,
                        default='',
                        help_text=(
                            'S3 key for the published isicRev4Taxonomy.js '
                            'bundle.'
                        ),
                        max_length=512,
                    ),
                ),
                ('section_count', models.PositiveIntegerField(default=0)),
                ('division_count', models.PositiveIntegerField(default=0)),
                ('group_count', models.PositiveIntegerField(default=0)),
                ('class_count', models.PositiveIntegerField(default=0)),
                (
                    'published_at',
                    models.DateTimeField(
                        blank=True,
                        help_text=(
                            'Timestamp when the active version was published.'
                        ),
                        null=True,
                    ),
                ),
                (
                    'last_error',
                    models.TextField(
                        blank=True,
                        default='',
                        help_text=(
                            'Human-readable failure from the most recent '
                            'publish attempt.'
                        ),
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'uploaded_by',
                    models.ForeignKey(
                        blank=True,
                        help_text=(
                            'Staff user who published the active taxonomy '
                            'version.'
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='isic_taxonomy_uploads',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'ISIC taxonomy',
                'verbose_name_plural': 'ISIC taxonomies',
            },
        ),
        RunPython(
            seed_isic_taxonomy_config,
            reverse_code=clear_isic_taxonomy_config,
        ),
    ]
