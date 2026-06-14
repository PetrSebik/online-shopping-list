import json

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse

from .models import Recipe, RecipeItem, RecipeStep, Tag


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    extra = 1


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 1


def _serialize_recipe(recipe):
    data = {"name": recipe.name}
    if recipe.description:
        data["description"] = recipe.description
    data["tags"] = [t.name for t in recipe.tags.all()]
    data["ingredients"] = []
    for item in recipe.items.all():
        ing = {"name": item.name}
        if item.count:
            ing["count"] = item.count
        if item.units:
            ing["units"] = item.units
        if item.description:
            ing["description"] = item.description
        data["ingredients"].append(ing)
    data["steps"] = [s.text for s in recipe.get_ordered_steps()]
    return data


def _build_schema(tag_names):
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "description": "Recipe import format",
        "type": "object",
        "required": ["name", "ingredients", "steps"],
        "properties": {
            "name": {"type": "string", "maxLength": 64},
            "description": {"type": "string", "maxLength": 512},
            "tags": {
                "type": "array",
                "items": {"type": "string", "enum": tag_names},
            },
            "ingredients": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string", "maxLength": 64},
                        "count": {"type": "integer", "minimum": 1, "description": "Omit entirely if there is no specific quantity"},
                        "units": {"type": "string", "maxLength": 8, "examples": ["g", "ml", "ks", "lžíce", "hrnek"]},
                        "description": {"type": "string", "maxLength": 128},
                    },
                },
            },
            "steps": {
                "type": "array",
                "minItems": 1,
                "description": "Cooking steps in order",
                "items": {"type": "string", "maxLength": 1024},
            },
        },
    }


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'last_cooked_date')
    inlines = [RecipeItemInline, RecipeStepInline]
    change_list_template = "admin/recipe/recipe/change_list.html"
    change_form_template = "admin/recipe/recipe/change_form.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('import/', self.admin_site.admin_view(self.import_view), name='recipe_recipe_import'),
        ]
        return custom + urls

    def import_view(self, request):
        tag_names = list(Tag.objects.order_by('name').values_list('name', flat=True))
        all_recipes = Recipe.objects.order_by('name').only('pk', 'name')
        schema_json = json.dumps(_build_schema(tag_names), ensure_ascii=False, indent=2)

        # Determine if we're editing an existing recipe
        recipe_id = request.GET.get('recipe') or request.POST.get('recipe_id') or ''
        selected_recipe = None
        if recipe_id:
            try:
                selected_recipe = Recipe.objects.prefetch_related('tags', 'items', 'steps').get(pk=recipe_id)
            except Recipe.DoesNotExist:
                recipe_id = ''

        json_data = ''

        if request.method == 'GET' and selected_recipe:
            json_data = json.dumps(_serialize_recipe(selected_recipe), ensure_ascii=False, indent=2)

        if request.method == 'POST':
            json_data = request.POST.get('json_data', '').strip()
            try:
                data = json.loads(json_data)

                if selected_recipe:
                    selected_recipe.name = data['name']
                    selected_recipe.description = data.get('description')
                    selected_recipe.save()
                    selected_recipe.items.all().delete()
                    selected_recipe.steps.all().delete()
                    recipe = selected_recipe
                    verb = 'uložen'
                else:
                    recipe = Recipe.objects.create(
                        name=data['name'],
                        description=data.get('description'),
                    )
                    verb = 'importován'

                tag_map = {t.name: t for t in Tag.objects.filter(name__in=data.get('tags', []))}
                recipe.tags.set([tag_map[n] for n in data.get('tags', []) if n in tag_map])
                skipped = [n for n in data.get('tags', []) if n not in tag_map]
                if skipped:
                    messages.warning(request, f"Neznámé tagy byly přeskočeny: {', '.join(skipped)}")

                for ingredient in data.get('ingredients', []):
                    RecipeItem.objects.create(
                        recipe=recipe,
                        name=ingredient['name'],
                        count=ingredient.get('count'),
                        units=ingredient.get('units'),
                        description=ingredient.get('description'),
                    )

                for i, step_text in enumerate(data.get('steps', []), start=1):
                    RecipeStep.objects.create(recipe=recipe, number=i, text=step_text)

                messages.success(request, f'Recept "{recipe.name}" byl úspěšně {verb}.')
                return HttpResponseRedirect(reverse('admin:recipe_recipe_change', args=[recipe.pk]))

            except (KeyError, ValueError) as e:
                messages.error(request, f"Import selhal: {e}")

        context = {
            **self.admin_site.each_context(request),
            'title': 'Upravit recept' if selected_recipe else 'Importovat recept',
            'schema_json': schema_json,
            'json_data': json_data,
            'all_recipes': all_recipes,
            'selected_recipe': selected_recipe,
            'selected_recipe_id': recipe_id,
        }
        return render(request, 'admin/recipe/import_recipe.html', context)


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color',)
