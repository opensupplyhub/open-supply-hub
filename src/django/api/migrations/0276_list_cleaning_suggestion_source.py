from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0275_list_cleaning_tour_dismissed'),
    ]

    operations = [
        migrations.AddField(
            model_name='listcleaningsuggestion',
            name='source',
            field=models.CharField(
                blank=True,
                default='',
                help_text='What produced the suggestion: rules, model or '
                          'rules+model (OSDEV-3724). Blank when the '
                          'pipeline did not say.',
                max_length=20),
        ),
    ]
