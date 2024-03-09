from django.forms import ModelForm
from .models import Recipe, RecipeItem, RecipeStep
from django.forms import inlineformset_factory


class RecipeItemForm(ModelForm):
    class Meta:
        model = RecipeItem
        fields = ['name', 'description', 'count', 'units']


class RecipeStepForm(ModelForm):
    class Meta:
        model = RecipeStep
        fields = ['number', 'text']


class CreateRecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['name']


RecipeItemFormSet = inlineformset_factory(Recipe, RecipeItem, form=RecipeItemForm, extra=1, can_delete=True)
RecipeStepFormSet = inlineformset_factory(Recipe, RecipeStep, form=RecipeStepForm, extra=1, can_delete=True)
