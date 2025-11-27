from django.urls import path
from .views import (
    RecipesListView,
    RecipesListFilteredView,
    RecipeDetailView,
    RecipeCreateView,
)

urlpatterns = [
    path('list/', RecipesListView.as_view(), name='recipes_list'),
    path('list/filtered/', RecipesListFilteredView.as_view(template_name='recipes_list_partial.html'),
         name='recipes_list_filtered'),
    path('detail/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'),
    path('create/', RecipeCreateView.as_view(), name='recipe_create'),
]
