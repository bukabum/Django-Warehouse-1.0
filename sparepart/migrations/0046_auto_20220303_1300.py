# Generated by Django 3.2 on 2022-03-03 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparepart', '0045_auto_20220228_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='Kecamatan',
            field=models.CharField(default=None, max_length=255, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='kota',
            field=models.CharField(default=None, max_length=255, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='provinsi',
            field=models.CharField(default=None, max_length=255, blank=True, null=True),
        ),
    ]
