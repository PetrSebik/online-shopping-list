# Generated by Django 4.2.5 on 2024-02-29 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipe", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="last_cooked_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
