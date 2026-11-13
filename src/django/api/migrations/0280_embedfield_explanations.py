from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Lets a contributor explain a field on their embedded map: what the
    field means, and what each of its values means. Empty on existing rows,
    so no embed changes.
    """

    dependencies = [
        ('api', '0279_embedconfig_spotlight'),
    ]

    operations = [
        migrations.AddField(
            model_name='embedfield',
            name='description',
            field=models.CharField(
                blank=True,
                default='',
                max_length=300,
                help_text='The contributor\'s explanation of what this '
                          'field means, shown with it on the embedded map.',
            ),
        ),
        migrations.AddField(
            model_name='embedfield',
            name='value_descriptions',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='The contributor\'s explanations of this field\'s '
                          'values, keyed by value.',
            ),
        ),
    ]
