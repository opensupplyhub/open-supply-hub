from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0273_list_cleaning_clean_close'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listcleaningrun',
            name='closed_reason',
            field=models.CharField(
                blank=True,
                choices=[('submitted', 'Contributor submitted'),
                         ('lapsed', 'Window lapsed, decisions so far applied'),
                         ('clean', 'Nothing to review, list as uploaded'),
                         ('failed', 'Run failed, list as uploaded')],
                default='', max_length=20),
        ),
    ]
