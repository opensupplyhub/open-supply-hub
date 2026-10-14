import django.contrib.postgres.fields
from django.db import migrations, models

# Current list + ('Cascale', 'Cascale').
#
# 'Sustainable Apparel Coalition' is deliberately retained: it is the string
# already stored on existing claims, and dropping it from the choices would
# invalidate those rows. The claim form no longer offers it, so only Cascale
# can be selected going forward. See OSDEV-2219.
AFFILIATION_CHOICES = [
        ('Benefits for Business and Workers (BBW)',
         'Benefits for Business and Workers (BBW)'),
        ('Better Mills Program', 'Better Mills Program'),
        ('Better Work (ILO)', 'Better Work (ILO)'),
        ('Canopy', 'Canopy'),
        ('Cascale', 'Cascale'),  # New option
        ('Ethical Trading Initiative', 'Ethical Trading Initiative'),
        ('Fair Labor Association', 'Fair Labor Association'),
        ('Fair Wear Foundation', 'Fair Wear Foundation'),
        ('HERfinance', 'HERfinance'),
        ('HERhealth', 'HERhealth'),
        ('HERrespect', 'HERrespect'),
        ('SEDEX', 'SEDEX'),
        ('Social and Labor Convergence Plan (SLCP)',
         'Social and Labor Convergence Plan (SLCP)'),
        ('Sustainable Apparel Coalition', 'Sustainable Apparel Coalition'),
        ('Sweatfree Purchasing Consortium', 'Sweatfree Purchasing Consortium'),
        ('ZDHC', 'ZDHC'),
]


class Migration(migrations.Migration):
    """
    Add Cascale to facility_affiliations choices.
    Django requires the full choices list in AlterField (no "append"
    operation); the DB column is unchanged (varchar array), only the app
    state is updated.
    """

    dependencies = [
        ('api', '0245_add_claim_quality_check_switch'),
    ]

    def _facility_affiliations_field():
        return django.contrib.postgres.fields.ArrayField(
            base_field=models.CharField(
                choices=AFFILIATION_CHOICES,
                help_text='A group the facility is affiliated with',
                max_length=50,
                verbose_name='facility affiliation',
            ),
            blank=True,
            help_text="The facility's affiliations",
            null=True,
            size=None,
            verbose_name='facility affilations',
        )

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='facilityclaim',
                    name='facility_affiliations',
                    field=_facility_affiliations_field(),
                ),
                migrations.AlterField(
                    model_name='historicalfacilityclaim',
                    name='facility_affiliations',
                    field=_facility_affiliations_field(),
                ),
            ],
        ),
    ]
