# Generated by Django 1.11.16 on 2019-06-17 16:38

from django.db import migrations

from custom.icds_reports.utils.migrations import get_view_migrations


class Migration(migrations.Migration):

    dependencies = [
        ('icds_reports', '0123_weighing_new_columng_agg_awc'),
    ]

    operations = get_view_migrations()