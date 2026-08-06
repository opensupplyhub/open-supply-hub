from django.db.migrations import Migration, AddField
from django.db.models import BooleanField


class Migration(Migration):

    dependencies = [
        ('api', '0212_add_moderation_pause_info_switch'),
    ]

    operations = [
        AddField(
            model_name='partnerfield',
            name='available_in_api',
            field=BooleanField(
                default=True,
                help_text=(
                    'Indicates if this partner field is available in the API.'
                ),
            ),
        ),
        AddField(
            model_name='partnerfield',
            name='available_in_data_downloads',
            field=BooleanField(
                default=True,
                help_text=(
                    'Indicates if this partner field is available in data '
                    'downloads.'
                ),
            ),
        ),
    ]
