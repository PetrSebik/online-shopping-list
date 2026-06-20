from django.urls import path
from .views import (
    RecipesListView,
    RecipesListFilteredView,
    RecipeDetailView,
    RecipeCreateView,
    RecipeCookedView,
)

urlpatterns = [
    path('list/', RecipesListView.as_view(), name='recipes_list'),
    path('list/filtered/', RecipesListFilteredView.as_view(),
         name='recipes_list_filtered'),
    path('detail/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'),
    path('detail/<int:pk>/cooked/', RecipeCookedView.as_view(), name='recipe_cooked'),
    path('create/', RecipeCreateView.as_view(), name='recipe_create'),
]
