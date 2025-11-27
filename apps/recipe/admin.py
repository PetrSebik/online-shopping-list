from django.contrib import admin

from .models import Recipe, RecipeItem, RecipeStep, Tag


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    extra = 1


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'last_cooked_date')
    inlines = [RecipeItemInline, RecipeStepInline]


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color',)
