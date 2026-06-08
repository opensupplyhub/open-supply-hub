from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0210_deactivate_rejected_list_sources'),
    ]

    operations = [
        migrations.AddField(
            model_name='moderationevent',
            name='os_id_snapshot',
            field=models.CharField(
                blank=True,
                default='',
                help_text=(
                    'Immutable snapshot of the OS ID set at approval time. '
                    'Survives facility deletion or merging, unlike the os FK.'
                ),
                max_length=32,
            ),
        ),
    ]
