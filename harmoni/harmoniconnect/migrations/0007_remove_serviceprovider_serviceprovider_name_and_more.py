# Generated by Django 4.1 on 2024-06-19 11:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("harmoniconnect", "0006_remove_serviceprovider_name_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="serviceprovider",
            name="serviceprovider_name",
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="name",
            field=models.CharField(default="Provider name", max_length=255),
        ),
    ]
