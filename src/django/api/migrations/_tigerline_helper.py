"""
Helper functions for US County Tigerline data migrations.
"""

import csv
import io
import os
import sys
import logging

import boto3
from django.conf import settings
from django.contrib.gis.geos import GEOSException, GEOSGeometry, MultiPolygon

logger = logging.getLogger(__name__)

csv.field_size_limit(sys.maxsize)


def get_s3_client():
    '''
    Create S3 client with MinIO support for local development.
    '''
    endpoint_url = os.getenv('AWS_S3_ENDPOINT_URL')

    if endpoint_url:
        # Local development with MinIO.
        return boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
        )
    else:
        # Production AWS S3.
        return boto3.client('s3')


def download_csv_from_s3(s3_key):
    '''
    Download the CSV file from S3 bucket.
    Returns the CSV content as a string.
    
    Args:
        s3_key: The S3 key/path to the CSV file (e.g., 'data/us_county_tigerline_2021.csv')
    '''
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    if not bucket_name:
        raise ValueError(
            'AWS_STORAGE_BUCKET_NAME is not configured. '
            'Cannot download CSV from S3.'
        )

    s3_client = get_s3_client()

    try:
        s3_client.head_object(Bucket=bucket_name, Key=s3_key)
    except s3_client.exceptions.NoSuchKey:
        raise ValueError(f'CSV file not found: {s3_key}')
    except Exception as e:
        raise Exception(f'Failed to check CSV file existence: {e}') from e

    response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
    return response['Body'].read().decode('utf-8')


def get_csv_reader(s3_key):
    '''
    Get CSV reader from S3 (or MinIO for local development).
    Returns CSV DictReader.
    
    Args:
        s3_key: The S3 key/path to the CSV file
    '''
    csv_content = download_csv_from_s3(s3_key)
    return csv.DictReader(io.StringIO(csv_content))


def parse_geometry(geometry_wkt, source_srid, target_srid=5070):
    '''
    Parse geometry from WKT and optionally transform to target SRID.
    
    Args:
        geometry_wkt: WKT string of the geometry
        source_srid: Source SRID (e.g., 4326 for WGS84, 5070 for Albers)
        target_srid: Target SRID (default: 5070)
    
    Returns:
        GEOSGeometry object in target_srid
    '''
    geom = GEOSGeometry(geometry_wkt, srid=source_srid)
    
    # Transform if source and target SRIDs differ.
    if source_srid != target_srid:
        geom.transform(target_srid)
    
    # Ensure MultiPolygon format.
    if geom.geom_type not in ("Polygon", "MultiPolygon"):
        raise ValueError(
            f'Unexpected geometry type: {geom.geom_type}'
        )
    
    if geom.geom_type == "Polygon":
        geom = MultiPolygon(geom, srid=target_srid)
    
    return geom


def populate_tigerline_data(
    apps_or_model,
    s3_key,
    source_srid=5070,
    clear_existing=False,
    production_envs=None
):
    '''
    Populate the USCountyTigerline table with data from CSV file.
    Works with both Django apps registry (for migrations) and model class (for management commands).
    
    Args:
        apps_or_model: Either Django apps registry (for migrations) or model class (for commands)
        s3_key: S3 key/path to the CSV file
        source_srid: SRID of the geometry data in CSV (default: 5070)
        clear_existing: Whether to clear existing data before populating
        production_envs: List of production environment names that require CSV (only for migrations)
    '''
    # Determine if apps_or_model is apps registry or model class.
    if hasattr(apps_or_model, 'get_model'):
        is_migration = True
        us_county_tigerline = apps_or_model.get_model('api', 'USCountyTigerline')
    else:
        is_migration = False
        us_county_tigerline = apps_or_model
    
    if clear_existing:
        us_county_tigerline.objects.all().delete()
    
    try:
        reader = get_csv_reader(s3_key)
    except Exception as e:
        logger.error(f'Failed to get CSV reader: {e}')

        if is_migration:
            env = os.getenv('DJANGO_ENV', 'Local')
            
            # Default production environments if not specified.
            if production_envs is None:
                production_envs = ['Production', 'Staging']
            
            if env not in production_envs:
                # In non-production environments, gracefully skip if CSV not found.
                return
            
            raise Exception(
                f'Failed to download CSV file from S3: {e}. '
                f'CSV file is required in {env} environment.'
            ) from e
        else:
            # For management commands, always raise the error.
            raise Exception(
                f'Failed to download CSV file from S3: {e}'
            ) from e
    
    tigerline_objects = []
    batch_size = 2000
    
    for row_num, row in enumerate(reader, start=1):
        geoid = row.get('geoid', '').strip()
        name = row.get('name', '').strip()
        geometry_wkt = row.get('geometry', '').strip()
        
        if not geoid or not name or not geometry_wkt:
            continue
        
        try:
            geom = parse_geometry(geometry_wkt, source_srid)
        except (ValueError, GEOSException) as e:
            # Log error but continue with other rows.
            logger.error(
                f'Error parsing geometry for {geoid} ({name}) '
                f'at row {row_num}: {e}'
            )
            continue
        
        tigerline_objects.append(
            us_county_tigerline(
                geoid=geoid,
                name=name,
                geometry=geom
            )
        )
        
        if len(tigerline_objects) >= batch_size:
            us_county_tigerline.objects.bulk_create(
                tigerline_objects,
                batch_size=batch_size
            )
            tigerline_objects = []
    
    if tigerline_objects:
        us_county_tigerline.objects.bulk_create(
            tigerline_objects,
            batch_size=batch_size
        )


def clear_tigerline_data(apps, schema_editor):
    '''
    Clear all existing USCountyTigerline data.
    '''
    us_county_tigerline = apps.get_model('api', 'USCountyTigerline')
    us_county_tigerline.objects.all().delete()

