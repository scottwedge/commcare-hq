# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-11 20:08
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime

import jsonfield.fields
import partial_index
from django.db import migrations, models

import corehq.blobs.models
import corehq.blobs.util
from corehq.sql_db.operations import RawSQLMigration


migrator = RawSQLMigration(('corehq', 'blobs', 'sql_templates'), {})


class Migration(migrations.Migration):

    dependencies = [
        ('blobs', '0001_squashed_0009_domains'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlobMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=255)),
                ('parent_id', models.CharField(help_text='Parent primary key or unique identifier', max_length=255)),
                ('name', models.CharField(default='', help_text='Optional blob name.\n\n        This field is intended to be used by doc types having multiple\n        blobs associated with a single document.\n        ', max_length=255),),
                ('path', models.CharField(default=corehq.blobs.models.uuid4_hex, help_text="Blob path in the external blob store.\n\n        This must be a globally unique value. Historically this was\n        `blob_bucket + '/' + identifier` for blobs associated with a\n        couch document. Could be a UUID or the result of\n        `util.random_url_id(16)`. Defaults to `uuid4().hex`.\n        ", max_length=255)),
                ('type_code', models.PositiveSmallIntegerField(help_text='Blob type code. See `corehq.blobs.CODES`.')),
                ('content_length', models.PositiveIntegerField()),
                ('content_type', models.CharField(max_length=255, null=True)),
                ('properties', corehq.blobs.util.NullJsonField(default=dict)),
                ('created_on', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('expires_on', models.DateTimeField(default=None, null=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='blobmeta',
            index=partial_index.PartialIndex(fields=['expires_on'], name='blobs_blobm_expires_64b92d_partial', unique=False, where='expires_on IS NOT NULL', where_postgresql=b'', where_sqlite=b''),
        ),
        migrations.AlterIndexTogether(
            name='blobmeta',
            index_together=set([('parent_id', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='blobmeta',
            unique_together=set([('path',)]),
        ),
        migrator.get_migration('get_blobmetas.sql'),
        migrator.get_migration('delete_blob_meta.sql'),
        migrator.get_migration('setup_blobmeta_view.sql', 'drop_blobmeta_view.sql'),
        # get_expired_blobs.sql must come after setup_blobmeta_view.sql
        migrator.get_migration('get_expired_blobs.sql'),
        migrator.get_migration('restrict_legacy_attachment_metadata_insert.sql', testing_only=True)
    ]
