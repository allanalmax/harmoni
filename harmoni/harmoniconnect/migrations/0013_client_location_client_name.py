# Generated by Django 4.2.13 on 2024-06-23 22:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("harmoniconnect", "0012_alter_client_user_alter_serviceprovider_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="location",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="client",
            name="name",
            field=models.CharField(default="Client name", max_length=255),
        ),
    ]
