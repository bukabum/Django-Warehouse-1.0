# Generated by Django 3.2 on 2022-02-27 04:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sparepart', '0039_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='person_responsible',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='alamat',
            field=models.CharField(max_length=255),
        ),
    ]
