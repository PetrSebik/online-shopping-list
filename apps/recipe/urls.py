from django.urls import path
from .views import (
    RecipesListView,
    RecipeDetailView,
    RecipeCreateView,
)

urlpatterns = [
    path('list/', RecipesListView.as_view(), name='recipes_list'),
    path('detail/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'),
    path('create/', RecipeCreateView.as_view(), name='recipe_create'),
]
