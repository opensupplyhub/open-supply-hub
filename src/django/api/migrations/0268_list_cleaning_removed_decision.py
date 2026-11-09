from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0267_list_cleaning_feedback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listcleaningsuggestion',
            name='decision',
            field=models.CharField(
                choices=[('PENDING', 'PENDING'), ('ACCEPTED', 'ACCEPTED'),
                         ('REJECTED', 'REJECTED'), ('EDITED', 'EDITED'),
                         ('REMOVED', 'REMOVED')],
                default='PENDING', max_length=20),
        ),
    ]
