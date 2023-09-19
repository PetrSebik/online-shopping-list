from django.urls import path
from .views import ShoppingListView, RemoveItemView

urlpatterns = [
    path('list/', ShoppingListView.as_view(), name='shopping_list'),
    path('remove-item/<int:item_id>/', RemoveItemView.as_view(), name='remove_item'),
]
