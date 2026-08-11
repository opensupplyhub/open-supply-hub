"""
Helper functions for ISIC taxonomy config data migrations.
"""

import json
import logging
import os
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from api.migrations._tigerline_helper import get_s3_client

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
ISIC_REV4_JSON_PATH = DATA_DIR / 'isic_rev4.json'

PRODUCTION_ENVS = ('Production', 'Staging')
TAXONOMY_S3_PREFIX = 'taxonomy/isic4'


def load_isic_rev4_taxonomy():
    with ISIC_REV4_JSON_PATH.open(encoding='utf-8') as taxonomy_file:
        return json.load(taxonomy_file)


def count_taxonomy_levels(taxonomy):
    sections = taxonomy.get('sections', [])
    division_count = 0
    group_count = 0
    class_count = 0

    for section in sections:
        for division in section.get('divisions', []):
            division_count += 1
            for group in division.get('groups', []):
                group_count += 1
                class_count += len(group.get('classes', []))

    return {
        'section_count': len(sections),
        'division_count': division_count,
        'group_count': group_count,
        'class_count': class_count,
    }


def generate_js_bundle(taxonomy):
    taxonomy_json = json.dumps(
        {'sections': taxonomy['sections']},
        ensure_ascii=False,
        indent=4,
    )
    return (
        'export const ISIC_REV4_TAXONOMY = Object.freeze(\n'
        f'    {taxonomy_json}\n'
        ');\n'
    )


def _artifact_s3_keys(version):
    prefix = f'{TAXONOMY_S3_PREFIX}/v{version}'
    return {
        'json_s3_key': f'{prefix}/isic_rev4.json',
        'bundle_s3_key': f'{prefix}/isicRev4Taxonomy.js',
    }


def upload_taxonomy_artifacts(version, taxonomy):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    if not bucket_name:
        raise ValueError(
            'AWS_STORAGE_BUCKET_NAME is not configured. '
            'Cannot upload ISIC taxonomy artifacts to S3.'
        )

    keys = _artifact_s3_keys(version)
    json_body = json.dumps(
        {'sections': taxonomy['sections']},
        ensure_ascii=False,
    ).encode('utf-8')
    js_body = generate_js_bundle(taxonomy).encode('utf-8')

    s3_client = get_s3_client()
    s3_client.put_object(
        Bucket=bucket_name,
        Key=keys['json_s3_key'],
        Body=json_body,
        ContentType='application/json',
    )
    s3_client.put_object(
        Bucket=bucket_name,
        Key=keys['bundle_s3_key'],
        Body=js_body,
        ContentType='application/javascript',
    )
    return keys


def seed_isic_taxonomy_config(apps, schema_editor):
    IsicTaxonomyConfig = apps.get_model('api', 'IsicTaxonomyConfig')

    if IsicTaxonomyConfig.objects.filter(pk=1).exists():
        return

    taxonomy = load_isic_rev4_taxonomy()
    counts = count_taxonomy_levels(taxonomy)
    version = 1
    json_s3_key = ''
    bundle_s3_key = ''

    try:
        keys = upload_taxonomy_artifacts(version, taxonomy)
        json_s3_key = keys['json_s3_key']
        bundle_s3_key = keys['bundle_s3_key']
    except Exception as exc:
        logger.error('Failed to upload ISIC taxonomy artifacts to S3: %s', exc)
        env = os.getenv('DJANGO_ENV', 'Local')
        if env in PRODUCTION_ENVS:
            raise Exception(
                'Failed to upload ISIC taxonomy artifacts to S3. '
                f'Upload is required in {env} environment.'
            ) from exc

    IsicTaxonomyConfig.objects.create(
        pk=1,
        is_active=True,
        version=version,
        json_s3_key=json_s3_key,
        bundle_s3_key=bundle_s3_key,
        published_at=timezone.now() if json_s3_key else None,
        **counts,
    )


def clear_isic_taxonomy_config(apps, schema_editor):
    IsicTaxonomyConfig = apps.get_model('api', 'IsicTaxonomyConfig')
    IsicTaxonomyConfig.objects.filter(pk=1).delete()
