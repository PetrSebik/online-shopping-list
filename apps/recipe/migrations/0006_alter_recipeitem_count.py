# Generated by Django 4.2.5 on 2024-03-09 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipe", "0005_alter_recipeitem_recipe_alter_recipestep_recipe"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipeitem",
            name="count",
            field=models.PositiveIntegerField(blank=True, default=1, null=True),
        ),
    ]
