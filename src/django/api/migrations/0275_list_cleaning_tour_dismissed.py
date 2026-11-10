from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0274_list_cleaning_failed_close'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listcleaningevent',
            name='kind',
            field=models.CharField(
                choices=[('opened', 'opened'), ('resumed', 'resumed'),
                         ('left', 'left'), ('submitted', 'submitted'),
                         ('lapsed', 'lapsed'),
                         ('tour_dismissed', 'tour_dismissed')],
                max_length=20),
        ),
    ]
