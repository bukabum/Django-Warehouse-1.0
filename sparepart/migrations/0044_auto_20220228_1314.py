# Generated by Django 3.2 on 2022-02-28 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparepart', '0043_order_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='kota',
            field=models.CharField(blank=True, null=True, default=None, max_length=255),
        ),
        migrations.AddField(
            model_name='customer',
            name='provinsi',
            field=models.CharField(blank=True, null=True, default=None, max_length=255),
        ),
    ]
