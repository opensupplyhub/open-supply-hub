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
                    'OS ID captured at first approval. Written once and '
                    'never overwritten; persists through facility deletion '
                    'or merging, unlike the os FK (on_delete=SET_NULL).'
                ),
                max_length=32,
            ),
        ),
    ]
