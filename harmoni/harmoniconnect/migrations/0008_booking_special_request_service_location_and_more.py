# Generated by Django 4.1 on 2024-06-20 11:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("harmoniconnect", "0007_remove_serviceprovider_serviceprovider_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="special_request",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="service",
            name="location",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="service",
            name="provider",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="services",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
