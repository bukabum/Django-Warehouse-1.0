# Generated by Django 3.2 on 2022-02-27 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparepart', '0040_auto_20220227_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='no_hp',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
