# Generated by Django 3.2 on 2022-02-18 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparepart', '0035_alter_sparepart_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sparepart',
            name='promo_price',
            field=models.PositiveBigIntegerField(blank=True, default=0, null=True),
        ),
    ]
