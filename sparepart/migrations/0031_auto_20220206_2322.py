# Generated by Django 3.2 on 2022-02-06 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparepart', '0030_orderitem_receipt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='receipt',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='total_price',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='use_discaunt',
            field=models.BooleanField(default=False),
        ),
    ]
