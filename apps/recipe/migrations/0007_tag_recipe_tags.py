# Generated by Django 5.2.1 on 2025-05-29 19:58

import colorfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipe", "0006_alter_recipeitem_count"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
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
                ("name", models.CharField(max_length=32)),
                (
                    "color",
                    colorfield.fields.ColorField(
                        default="#FF0000", image_field=None, max_length=25, samples=None
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="recipe",
            name="tags",
            field=models.ManyToManyField(blank=True, to="recipe.tag"),
        ),
    ]
