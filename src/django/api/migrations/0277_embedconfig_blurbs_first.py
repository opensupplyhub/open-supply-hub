from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Lets a contributor list the facilities that have a blurb first on their
    embedded map. Off by default, so no existing embed changes its order.
    """

    dependencies = [
        ('api', '0276_embedconfig_marker_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='embedconfig',
            name='blurbs_first',
            field=models.BooleanField(
                default=False,
                help_text='Whether facilities that have a blurb are listed '
                          'first on the embedded map, ahead of the chosen '
                          'list order.',
            ),
        ),
    ]
