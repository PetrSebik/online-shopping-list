from django.urls import path
from .views import (
    ShoppingListView,
    RemoveItemView,
    AddItemRestView,
    RemoveItemRestView,
    ListItemsRestView,
    HTMXShoppingBaseView,
    HTMXShoppingListView,
    HTMXShoppingAddItemView,
)

urlpatterns = [
    path('list/', ShoppingListView.as_view(), name='shopping_list'),
    path('remove-item/<int:item_id>/', RemoveItemView.as_view(), name='remove_item'),
    path('item/', AddItemRestView.as_view(), name='rest_add_item'),
    path('item/<int:pk>/', RemoveItemRestView.as_view(), name='rest_remove_item'),
    path('items/list/', ListItemsRestView.as_view(), name='rest_item_view'),
    path('htmx/base/', HTMXShoppingBaseView.as_view(), name='htmx_shopping'),
    path('htmx/list/', HTMXShoppingListView.as_view(), name='htmx_shopping_list'),
    path('htmx/item/', HTMXShoppingAddItemView.as_view(), name='htmx_shopping_item'),
]
