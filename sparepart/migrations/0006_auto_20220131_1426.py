# Generated by Django 3.2 on 2022-01-31 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sparepart', '0005_auto_20220131_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='sparepart',
            name='date_added',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sparepart',
            name='update_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
