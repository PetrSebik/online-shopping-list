# Generated by Django 4.2.5 on 2024-03-09 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipe", "0003_recipestep_recipeitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipeitem",
            name="description",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
