# Generated by Django 3.2 on 2022-02-01 02:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sparepart', '0007_auto_20220201_0923'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stockin',
            old_name='Descripion',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='stockin',
            old_name='StockIn',
            new_name='stockin',
        ),
        migrations.RenameField(
            model_name='stockout',
            old_name='Descripion',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='stockout',
            old_name='StockOut',
            new_name='stockout',
        ),
    ]
