import os
from django.db import connection
from django.db import migrations

SQL_DIRECTORY = './sqls/'


def execute_sql_from_file(file_name):
    file_path = os.path.join(SQL_DIRECTORY, file_name)
    with open(file_path, 'r') as file:
        sql_statement = file.read()
    with connection.cursor() as cursor:
        cursor.execute(sql_statement)


def create_strip_all_triggers_proc(apps, schema_editor):
    execute_sql_from_file('strip_all_triggers.sql')


def drop_strip_all_triggers_proc(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute('DROP procedure IF EXISTS strip_all_triggers;')


def create_remove_items_where_facility_id_is_null_proc(apps, schema_editor):
    execute_sql_from_file('remove_items_where_facility_id_is_null.sql')


def drop_remove_items_where_facility_id_is_null_proc(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            'DROP procedure IF EXISTS remove_items_where_facility_id_is_null;'
        )


def create_remove_old_pending_matches_proc(apps, schema_editor):
    execute_sql_from_file('remove_old_pending_matches.sql')


def drop_remove_old_pending_matches_proc(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            'DROP procedure IF EXISTS ' 'remove_old_pending_matches;'
        )


def create_remove_items_without_matches_and_related_facilities_proc(
    apps, schema_editor
):
    execute_sql_from_file(
        'remove_items_without_matches_and_related_facilities.sql'
    )


def drop_remove_items_without_matches_and_related_facilities_proc(
    apps, schema_editor
):
    with connection.cursor() as cursor:
        cursor.execute(
            'DROP procedure IF EXISTS '
            'remove_items_without_matches_and_related_facilities;'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0144_remove_unnecessary_columns_from_facility_claim'),
    ]

    operations = [
        migrations.RunPython(
            create_strip_all_triggers_proc,
            drop_strip_all_triggers_proc,
        ),
        migrations.RunPython(
            create_remove_items_where_facility_id_is_null_proc,
            drop_remove_items_where_facility_id_is_null_proc,
        ),
        migrations.RunPython(
            create_remove_old_pending_matches_proc,
            drop_remove_old_pending_matches_proc,
        ),
        migrations.RunPython(
            create_remove_items_without_matches_and_related_facilities_proc,
            drop_remove_items_without_matches_and_related_facilities_proc,
        ),
    ]
