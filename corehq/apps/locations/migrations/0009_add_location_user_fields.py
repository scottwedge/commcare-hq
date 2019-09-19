# Generated by Django 1.10.6 on 2017-03-31 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0008_increase_name_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationtype',
            name='has_user',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sqllocation',
            name='user_id',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
