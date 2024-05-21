import os
from django.db import connection
from django.db import migrations


def create_strip_all_triggers_procedure(apps, schema_editor):
    file_path = os.path.join('./sqls/', 'strip_all_triggers.sql')
    sql_statement = open(file_path).read()
    with connection.cursor() as c:
        c.execute(sql_statement)


def drop_strip_all_triggers_procedure(apps, schema_editor):
    with connection.cursor() as c:
        c.execute('drop procedure strip_all_triggers;')


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0144_remove_unnecessary_columns_from_facility_claim'),
    ]

    operations = [
        migrations.RunPython(
            create_strip_all_triggers_procedure,
            drop_strip_all_triggers_procedure
        ),
    ]
