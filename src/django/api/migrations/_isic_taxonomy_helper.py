"""
Helper functions for ISIC taxonomy config data migrations.
"""


def seed_isic_taxonomy_config(apps, _schema_editor):
    isic_taxonomy_config_model = apps.get_model('api', 'IsicTaxonomyConfig')

    if isic_taxonomy_config_model.objects.filter(pk=1).exists():
        return

    isic_taxonomy_config_model.objects.create(
        pk=1,
        is_active=False,
        version=0,
        json_s3_key='',
        bundle_s3_key='',
    )


def clear_isic_taxonomy_config(apps, _schema_editor):
    isic_taxonomy_config_model = apps.get_model('api', 'IsicTaxonomyConfig')
    isic_taxonomy_config_model.objects.filter(pk=1).delete()
