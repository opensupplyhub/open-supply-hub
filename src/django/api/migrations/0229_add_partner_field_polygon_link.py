import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Add the polygon link column to partner fields."""

    dependencies = [
        ('api', '0228_create_polygon'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnerfield',
            name='polygon',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='partner_fields',
                to='api.polygon',
                help_text=(
                    'For polygon-driven system fields: the boundary '
                    'whose covered locations receive this field. '
                    'Deleting a polygon that a field points at is '
                    'blocked by the database.'
                ),
            ),
        ),
    ]
