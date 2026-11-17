from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adds `last_upload_sha256` to api_zoneset: the digest of the GeoJSON
    file the set's zones were last stored from, which the admin form
    reads to refuse adding the same file twice (OSDEV-3812). A column
    with a constant default (the empty string, meaning "no upload
    recorded yet"), so no row is rewritten and every existing set
    behaves as before until its next upload. Runs under the same 5 s
    `lock_timeout` as 0274 because the provider registry reads
    api_zoneset on every location page. Also rewords `help_text` on
    `api_zone.feature_index`, which is a model-state change only and
    emits no SQL. The reverse drops the column.
    """

    dependencies = [
        ('api', '0283_list_cleaning_pipeline_meta'),
    ]

    operations = [
        migrations.RunSQL(
            sql="SET LOCAL lock_timeout = '5s';",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AddField(
            model_name='zoneset',
            name='last_upload_sha256',
            field=models.CharField(
                blank=True,
                default='',
                editable=False,
                help_text=(
                    'SHA-256 digest of the GeoJSON file the zones were '
                    'last stored from, by a replace or an add. The '
                    'admin form refuses to add a file with this '
                    'digest, so a double-click or a resubmitted page '
                    'cannot store the same zones twice. Only the last '
                    'upload is remembered: a file added before it is '
                    'not recognised.'
                ),
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name='zone',
            name='feature_index',
            field=models.PositiveIntegerField(
                help_text=(
                    'Position of the source feature across the set\'s '
                    'uploads (0-based): its position in the file for '
                    'the set\'s first or replacing upload, continuing '
                    'after the stored maximum for a file added to the '
                    'set. When zones in a set overlap, the lowest '
                    'index wins.'
                ),
            ),
        ),
    ]
