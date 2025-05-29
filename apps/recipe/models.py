from colorfield.fields import ColorField
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=32)
    color = ColorField(default="#FF0000")

    @property
    def text_color(self) -> str:
        """Returns black or white depending on the brightness of the background color."""
        hex_color = self.color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return '#000000' if brightness > 128 else '#ffffff'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=512, blank=True, null=True)
    last_cooked_date = models.DateField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def get_ordered_steps(self):
        return self.steps.order_by('number').all()


class RecipeItem(models.Model):
    recipe = models.ForeignKey("recipe.Recipe", on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128, blank=True, null=True)
    count = models.PositiveIntegerField(default=1, blank=True, null=True)
    units = models.CharField(max_length=8, null=True, blank=True)


class RecipeStep(models.Model):
    recipe = models.ForeignKey("recipe.Recipe", on_delete=models.CASCADE, related_name="steps")
    number = models.PositiveIntegerField(default=1)
    text = models.CharField(max_length=256)
