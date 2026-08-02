from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Recipe = apps.get_model("recipe", "Recipe")
    seen = set()
    for recipe in Recipe.objects.order_by("id"):
        base = slugify(recipe.name) or "recept"
        slug = base
        suffix = 2
        while slug in seen or Recipe.objects.filter(slug=slug).exclude(pk=recipe.pk).exists():
            slug = f"{base}-{suffix}"
            suffix += 1
        seen.add(slug)
        recipe.slug = slug
        recipe.save(update_fields=["slug"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("recipe", "0009_tracking_and_units"),
    ]

    operations = [
        # Added without unique=True first — existing rows would otherwise all
        # collide on the same "" default the moment the column is created.
        migrations.AddField(
            model_name="recipe",
            name="slug",
            field=models.SlugField(max_length=90, blank=True, default=""),
            preserve_default=False,
        ),
        migrations.RunPython(populate_slugs, noop),
        migrations.AlterField(
            model_name="recipe",
            name="slug",
            field=models.SlugField(max_length=90, blank=True, unique=True),
        ),
    ]
