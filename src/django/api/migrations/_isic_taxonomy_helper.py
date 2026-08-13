"""
Helper functions for ISIC taxonomy config data migrations.
"""


def seed_isic_taxonomy_config(apps, schema_editor):
    IsicTaxonomyConfig = apps.get_model('api', 'IsicTaxonomyConfig')

    if IsicTaxonomyConfig.objects.filter(pk=1).exists():
        return

    IsicTaxonomyConfig.objects.create(
        pk=1,
        is_active=False,
        version=0,
        json_s3_key='',
        bundle_s3_key='',
    )


def clear_isic_taxonomy_config(apps, schema_editor):
    IsicTaxonomyConfig = apps.get_model('api', 'IsicTaxonomyConfig')
    IsicTaxonomyConfig.objects.filter(pk=1).delete()
