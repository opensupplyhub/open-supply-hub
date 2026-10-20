from django.db import migrations

from api.helpers.claim_profile_options import rename_claim_option_value

# The lists the claim form offered before this migration, in the order it
# offered them. Sort orders are spaced by 10 so staff can slot new options
# in between without renumbering.
AFFILIATIONS = [
    'Benefits for Business and Workers (BBW)',
    'Better Mills Program',
    'Better Work (ILO)',
    'Canopy',
    'Cascale',
    'Ethical Trading Initiative',
    'Fair Labor Association',
    'Fair Wear Foundation',
    'HERfinance',
    'HERhealth',
    'HERrespect',
    'SEDEX',
    'Social and Labor Convergence Plan (SLCP)',
    'Sweatfree Purchasing Consortium',
    'ZDHC',
]

# Defined as a constant but never offered by the claim form; seeded
# inactive so it keeps not being offered until staff switch it on.
INACTIVE_AFFILIATIONS = [
    'European Outdoor Group',
]

CERTIFICATIONS = [
    'BCI',
    'B Corp',
    'Bluesign',
    'Canopy',
    'Cradle to Cradle',
    'EU Ecolabel',
    'Fairtrade USA',
    'FSC',
    'Global Recycling Standard (GRS)',
    'GOTS',
    'Green Button',
    'Green Screen for Safer Chemicals',
    'Higg Index',
    'IMO Control',
    'International Wool Textile Organisation (IWTO)',
    'ISO 9000',
    'IVN leather',
    'Leather Working Group',
    'Nordic Swan',
    'Oeko-Tex Standard 100',
    'Oeko-Tex STeP',
    'Oeko-Tex Eco Passport',
    'Oeko-Tex Made in Green',
    'PEFC',
    'REACH',
    'Responsible Down Standard (RDS)',
    'Responsible Wool Standard (RWS)',
    'Rainforest Alliance',
    'SA8000',
    'ABVTEX',
    'Empresa B',
    'Origem Sustentável',
    'Selo ABR',
]

# The Sustainable Apparel Coalition rebranded to Cascale. 0246 stopped
# offering the old name; this rewrites the claims that still hold it.
SUPERSEDED_AFFILIATIONS = {
    'Sustainable Apparel Coalition': 'Cascale',
}


def _stored_values(connection, column):
    with connection.cursor() as cursor:
        cursor.execute(
            f'SELECT DISTINCT unnest({column}) FROM api_facilityclaim'
        )
        return {row[0] for row in cursor.fetchall() if row[0]}


def _seed(model, connection, column, active, inactive=()):
    rows = [
        model(name=name, is_active=True, sort_order=(index + 1) * 10)
        for index, name in enumerate(active)
    ]
    known = {name.lower() for name in active}
    next_order = (len(active) + 1) * 10
    # Any other value a claim already stores becomes an inactive option,
    # so every stored value has a row staff can see, rename or reactivate.
    # Names are unique ignoring case, so only the first spelling is kept.
    for name in sorted(set(inactive) | _stored_values(connection, column)):
        if name.lower() in known:
            continue
        known.add(name.lower())
        rows.append(
            model(name=name, is_active=False, sort_order=next_order)
        )
    model.objects.bulk_create(rows)


def seed_options(apps, schema_editor):
    connection = schema_editor.connection

    for old_name, new_name in SUPERSEDED_AFFILIATIONS.items():
        rename_claim_option_value(
            connection, 'facility_affiliations', old_name, new_name
        )

    _seed(
        apps.get_model('api', 'ClaimAffiliation'),
        connection,
        'facility_affiliations',
        AFFILIATIONS,
        INACTIVE_AFFILIATIONS,
    )
    _seed(
        apps.get_model('api', 'ClaimCertification'),
        connection,
        'facility_certifications',
        CERTIFICATIONS,
    )


def unseed_options(apps, schema_editor):
    # The Cascale rename is not reverted: claims that held Cascale before
    # this migration cannot be told apart from rewritten ones.
    apps.get_model('api', 'ClaimAffiliation').objects.all().delete()
    apps.get_model('api', 'ClaimCertification').objects.all().delete()


class Migration(migrations.Migration):
    """
    Seed the claim affiliation and certification options with the lists
    the claim form offered until now, and rewrite "Sustainable Apparel
    Coalition" to "Cascale" on existing claims (and their history), bumping
    `updated_at` on the affected facilities so the OpenSearch sync picks
    the change up. See OSDEV-2219.
    """

    dependencies = [
        ('api', '0248_add_claim_profile_options'),
    ]

    operations = [
        migrations.RunPython(seed_options, unseed_options),
    ]
