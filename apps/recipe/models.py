from django.db import models


class Recipe(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=512, blank=True, null=True)
    last_cooked_date = models.DateField(blank=True, null=True)

    def get_ordered_steps(self):
        return self.steps.order_by('number').all()


class RecipeItem(models.Model):
    recipe = models.ForeignKey("recipe.Recipe", on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128, blank=True, null=True)
    count = models.PositiveIntegerField(default=1)
    units = models.CharField(max_length=8, null=True, blank=True)


class RecipeStep(models.Model):
    recipe = models.ForeignKey("recipe.Recipe", on_delete=models.CASCADE, related_name="steps")
    number = models.PositiveIntegerField(default=1)
    text = models.CharField(max_length=256)
