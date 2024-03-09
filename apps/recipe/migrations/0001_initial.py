# Generated by Django 4.2.5 on 2024-02-29 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                (
                    "description",
                    models.CharField(blank=True, max_length=512, null=True),
                ),
                ("last_cooked_date", models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]