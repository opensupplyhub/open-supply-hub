from django.db import migrations, models
import django.db.models.deletion


NAME_HELP_TEXT = (
    'The official English facility name asserted by the claimant. Editable '
    'through the claim form and the claimed-details form; promoted on the '
    'production location page while the claim is approved.'
)

ADDRESS_HELP_TEXT = (
    'The facility address asserted by the claimant. Editable through the '
    'claim form and the claimed-details form; promoted on the production '
    'location page while the claim is approved.'
)

CLAIM_HELP_TEXT = (
    'The facility claim a CLAIM event records a contribution for. One claim '
    'produces several events over its life: one when the claim is approved '
    'and one for each later name or address edit the claimant makes, so this '
    'is a plain foreign key.'
)


def claim_text_field(help_text, verbose_name):
    return models.CharField(
        blank=True,
        help_text=help_text,
        max_length=200,
        null=True,
        verbose_name=verbose_name,
    )


class Migration(migrations.Migration):
    """
    Claim contribution moderation events (OSDEV-3510; fields on the claim in
    OSDEV-3405, frontend in OSDEV-3404).

    ModerationEvent.claim becomes a plain foreign key: a claim now produces
    one CLAIM-type event when it is approved and another for every later
    name or address edit by the claimant, so the one-to-one no longer holds.
    Nothing reads the reverse relation, whose name changes to
    `moderation_events`.

    The help text on FacilityClaim.facility_name_english and
    facility_address still described them as not editable, which has been
    untrue since the claimed-details form started writing them; the text is
    updated on the model and its history table. No data changes.
    """

    dependencies = [
        ('api', '0241_add_claim_name_address_edit_switch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facilityclaim',
            name='facility_address',
            field=claim_text_field(ADDRESS_HELP_TEXT, 'address'),
        ),
        migrations.AlterField(
            model_name='facilityclaim',
            name='facility_name_english',
            field=claim_text_field(
                NAME_HELP_TEXT, 'facility name in English'
            ),
        ),
        migrations.AlterField(
            model_name='historicalfacilityclaim',
            name='facility_address',
            field=claim_text_field(ADDRESS_HELP_TEXT, 'address'),
        ),
        migrations.AlterField(
            model_name='historicalfacilityclaim',
            name='facility_name_english',
            field=claim_text_field(
                NAME_HELP_TEXT, 'facility name in English'
            ),
        ),
        migrations.AlterField(
            model_name='moderationevent',
            name='claim',
            field=models.ForeignKey(
                blank=True,
                help_text=CLAIM_HELP_TEXT,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='moderation_events',
                to='api.facilityclaim',
            ),
        ),
    ]
