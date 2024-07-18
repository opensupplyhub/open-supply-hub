from django.db import migrations, models
from api.models import SectorGroup


def populate_sector_groups(apps, schema_editor):
    groups_names = [
        "Apparel, Footwear, Textiles",
        "Agriculture, Food & Beverage",
        "Technology",
        "Automotive",
        "Electronics",
        "Energy",
        "Utilities",
        "Mining",
        "Construction",
        "Cosmetics",
        "Durable Goods",
        "Transportation",
        "Aerospace",
        "Forestry",
        "Press",
        "Health",
        "Entertainment",
        "Accommodation",
        "Governmental",
        "Finance",
        "General Merchandise",
        "Storage",
        "Sporting Goods",
        "Education, Research, Services",
        "Other",
    ]

    for name in groups_names:
        SectorGroup.objects.create(name=name)


class Migration(migrations.Migration):
    '''
    This migration creates the SectorGroup model and populates it with
    the sector groups names.
    '''

    initial = True

    dependencies = [
        ('api', '0150_introduce_function_formatting_number_to_percent'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectorGroup',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.RunPython(populate_sector_groups),
    ]
