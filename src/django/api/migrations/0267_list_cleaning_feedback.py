from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

SWITCH_NAME = 'enable_list_cleaning_feedback'


def create_switch(apps, schema_editor):
    switch_model = apps.get_model('waffle', 'Switch')
    switch_model.objects.get_or_create(name=SWITCH_NAME,
                                       defaults={'active': False})


def delete_switch(apps, schema_editor):
    switch_model = apps.get_model('waffle', 'Switch')
    switch_model.objects.filter(name=SWITCH_NAME).delete()


class Migration(migrations.Migration):
    """
    OSDEV-3726: store list-cleaning pipeline runs and per-row suggestions
    against a facility list, and add the `enable_list_cleaning_feedback`
    switch (created inactive) that gates the whole feature.
    """

    dependencies = [
        ('api', '0266_announcement_banner'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListCleaningRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('RUNNING', 'RUNNING'), ('COMPLETE', 'COMPLETE'), ('FAILED', 'FAILED')], default='PENDING', max_length=20)),
                ('runner', models.CharField(choices=[('stepfunctions', 'AWS Step Functions'), ('stub', 'Local stub rules'), ('import', 'Imported records file')], default='stepfunctions', help_text='What executed the pipeline for this run.', max_length=20)),
                ('execution_arn', models.CharField(blank=True, default='', help_text='Step Functions execution ARN, when the runner is stepfunctions.', max_length=512)),
                ('prompt_version', models.CharField(blank=True, default='', help_text='PromptVersion the pipeline reported for this run.', max_length=20)),
                ('file_pass', models.JSONField(blank=True, default=dict, help_text='List-level findings from stage 1: header issues, repeated names, exact duplicates.')),
                ('usage', models.JSONField(blank=True, default=dict, help_text='Token usage and wall-clock reported by the pipeline.')),
                ('error', models.TextField(blank=True, default='', help_text='Why the run failed, if it did.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('applied_at', models.DateTimeField(blank=True, help_text='When accepted corrections were last applied to the list.', null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ListCleaningSuggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row_number', models.IntegerField(help_text='Row number as in the spreadsheet (first data row is 2).')),
                ('kind', models.CharField(choices=[('CORRECTION', 'Suggested correction'), ('ISSUE', 'Issue'), ('REMOVAL', 'Row removal')], max_length=20)),
                ('field', models.CharField(blank=True, default='', help_text='Column the suggestion applies to, when it is one column.', max_length=100)),
                ('code', models.CharField(help_text='Reason code (corrections) or issue code (issues) from the prompt catalog. Several codes joined by "+" when the model applied more than one rule to a field.', max_length=100)),
                ('severity', models.CharField(blank=True, choices=[('must_fix', 'must_fix'), ('internal_note', 'internal_note')], default='', help_text='Issues only. internal_note is never shown to the contributor.', max_length=20)),
                ('original_value', models.TextField(blank=True, default='')),
                ('corrected_value', models.TextField(blank=True, default='')),
                ('note', models.TextField(blank=True, default='', help_text='The one-sentence plain-language explanation.')),
                ('extra', models.JSONField(blank=True, default=dict, help_text='Anything else the record carried, e.g. duplicate_of.')),
                ('decision', models.CharField(choices=[('PENDING', 'PENDING'), ('ACCEPTED', 'ACCEPTED'), ('REJECTED', 'REJECTED'), ('EDITED', 'EDITED')], default='PENDING', max_length=20)),
                ('decided_value', models.TextField(blank=True, default='', help_text='The value the contributor typed, when decision is EDITED.')),
                ('decided_at', models.DateTimeField(blank=True, null=True)),
                ('applied', models.BooleanField(default=False, help_text='Whether this correction has been written to the list item.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['row_number', 'id'],
            },
        ),
        migrations.AddField(
            model_name='listcleaningrun',
            name='facility_list',
            field=models.ForeignKey(help_text='The list this run was started for.', on_delete=django.db.models.deletion.CASCADE, related_name='cleaning_runs', to='api.facilitylist'),
        ),
        migrations.AddField(
            model_name='listcleaningsuggestion',
            name='decided_by',
            field=models.ForeignKey(blank=True, help_text='Null when the decision was the default the system applied (pre-accepted silent corrections).', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='listcleaningsuggestion',
            name='facility_list_item',
            field=models.ForeignKey(blank=True, help_text='The row this suggestion is about. Null for findings the pipeline reported for a row that has no item.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cleaning_suggestions', to='api.facilitylistitem'),
        ),
        migrations.AddField(
            model_name='listcleaningsuggestion',
            name='run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggestions', to='api.listcleaningrun'),
        ),
        migrations.AddIndex(
            model_name='listcleaningsuggestion',
            index=models.Index(fields=['run', 'row_number'], name='api_lcs_run_row_idx'),
        ),
        migrations.RunPython(create_switch, delete_switch),
    ]
