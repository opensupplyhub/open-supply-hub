# Generated by Django 3.2.17 on 2025-01-14 11:17

from django.db.migrations import Migration, RunPython
from django.db import connection
from api.migrations._migration_helper import MigrationHelper

helper = MigrationHelper(connection)


def perform_upgrading_pg_extensions(apps, schema_editor):
    helper.run_sql_files([
        '0163_upgrade_postgres_extensions.sql'
    ])


class Migration(Migration):
    '''
    This migration upgrades the PostgreSQL database extension versions.

    Currently, the database uses the following extensions:
    1. postgis
    2. unaccent
    3. pg_trgm
    4. plpgsql
    5. btree_gin
    6. pgcrypto

    Based on the available extension versions for PostgreSQL 13.15 in AWS RDS,
    which will be used across all AWS environments after the database upgrade,
    it was found that the `postgis` extension can be upgraded to version 3.4.2
    in Production and Staging. Additionally, the `pg_trgm` extension can be
    upgraded to version 1.5 in Development, Test, Production, and Staging.
    If the specified versions are already installed in the database, there
    will be no issues.
    '''

    dependencies = [
        ('api', '0162_update_moderationevent_table_fields'),
    ]

    operations = [
        RunPython(perform_upgrading_pg_extensions)
    ]
