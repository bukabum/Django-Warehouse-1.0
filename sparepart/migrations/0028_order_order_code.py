# Generated by Django 3.2 on 2022-02-06 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparepart', '0027_auto_20220206_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_code',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
