from django.urls import path
from .views import (
    RecipesListView,
    RecipesListFilteredView,
    RecipeDetailView,
    RecipeCreateView,
    RecipeCookedView,
    RecipeToggleTrackingView,
    AddRecipeToShoppingListView,
)

urlpatterns = [
    path('list/', RecipesListView.as_view(), name='recipes_list'),
    path('list/filtered/', RecipesListFilteredView.as_view(),
         name='recipes_list_filtered'),
    path('detail/<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'),
    path('detail/<int:pk>/cooked/', RecipeCookedView.as_view(), name='recipe_cooked'),
    path('detail/<int:pk>/toggle-tracking/', RecipeToggleTrackingView.as_view(), name='recipe_toggle_tracking'),
    path('detail/<int:pk>/add-to-list/', AddRecipeToShoppingListView.as_view(), name='recipe_add_to_list'),
    path('create/', RecipeCreateView.as_view(), name='recipe_create'),
]
