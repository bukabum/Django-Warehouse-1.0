# Generated by Django 3.2 on 2022-01-31 07:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sparepart', '0004_auto_20220131_1424'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sparepart',
            name='date_added',
        ),
        migrations.RemoveField(
            model_name='sparepart',
            name='update_date',
        ),
    ]
