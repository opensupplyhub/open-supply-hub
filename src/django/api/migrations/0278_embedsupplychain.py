import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Creates the table for the supply chains a contributor puts together
    from their own facilities to show on their embedded map.
    """

    dependencies = [
        ('api', '0277_embedconfig_blurbs_first'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmbedSupplyChain',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('name', models.CharField(
                    help_text='The name shown to visitors, such as a '
                              'product line.',
                    max_length=200)),
                ('description', models.TextField(
                    blank=True, default='',
                    help_text='A short description shown to visitors.',
                    max_length=600)),
                ('product_url', models.CharField(
                    blank=True, default='',
                    help_text='A link to the product this supply chain '
                              'makes.',
                    max_length=500,
                    validators=[django.core.validators.URLValidator(
                        schemes=['http', 'https'])])),
                ('color', models.CharField(
                    default='#c0392b',
                    help_text='The color of this supply chain on the map.',
                    max_length=7,
                    validators=[django.core.validators.RegexValidator(
                        message='Enter a color as a six-digit hex value, '
                                'for example #1386c6.',
                        regex='^#[0-9a-fA-F]{6}$')])),
                ('is_published', models.BooleanField(
                    default=False,
                    help_text='Whether visitors to the embedded map can '
                              'see this supply chain.')),
                ('order', models.PositiveSmallIntegerField(
                    default=0,
                    help_text="The position of this supply chain among "
                              "the contributor's supply chains.")),
                ('nodes', models.JSONField(
                    blank=True, default=list,
                    help_text='The locations in this supply chain, as '
                              '[{"os_id": ..., "stage": ...}].')),
                ('links', models.JSONField(
                    blank=True, default=list,
                    help_text='Which location supplies which, as '
                              '[[supplier OS ID, customer OS ID]].')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('contributor', models.ForeignKey(
                    help_text='The contributor who owns this supply chain.',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='embed_supply_chains',
                    to='api.contributor')),
            ],
            options={
                'ordering': ('order', 'id'),
            },
        ),
    ]
