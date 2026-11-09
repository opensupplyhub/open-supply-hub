from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0267_list_cleaning_advisory_severity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listcleaningrun',
            name='closed_reason',
            field=models.CharField(
                blank=True,
                choices=[('submitted', 'Contributor submitted'),
                         ('lapsed', 'Window lapsed, list as uploaded'),
                         ('clean', 'Nothing to review, list as uploaded')],
                default='', max_length=20),
        ),
    ]
