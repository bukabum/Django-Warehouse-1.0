# Generated by Django 3.2 on 2022-02-02 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparepart', '0015_historicalsparepart'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsparepart',
            name='first_stock',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='sparepart',
            name='first_stock',
            field=models.IntegerField(default=0),
        ),
    ]
