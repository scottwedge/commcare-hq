# Generated by Django 1.10.7 on 2017-07-06 21:18

from django.db import migrations

from corehq.sql_db.operations import RawSQLMigration

migrator = RawSQLMigration(('corehq', 'sql_accessors', 'sql_templates'), {})


class Migration(migrations.Migration):

    dependencies = [
        ('sql_accessors', '0048_livequery_sql'),
    ]

    operations = [
        migrations.RunSQL("""DROP FUNCTION IF EXISTS save_case_and_related_models(
                TEXT,
                form_processor_commcarecasesql,
                form_processor_casetransaction[],
                form_processor_commcarecaseindexsql[],
                form_processor_caseattachmentsql[],
                INTEGER[],
                INTEGER[])"""
                 )
    ]
