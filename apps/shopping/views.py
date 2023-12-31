from django.shortcuts import redirect
from django.views import View
from django.views.generic.edit import FormView
from rest_framework import generics
from .forms import AddItemForm
from .models import Item
from .serializers import ItemSerializer


class ShoppingListView(FormView):
    template_name = 'shopping.html'
    form_class = AddItemForm
    success_url = '/shopping/list/'

    def form_valid(self, form):
        form.save(commit=True)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shopping_list'] = Item.objects.all()
        return context


class RemoveItemView(View):
    def get(self, request, item_id, *args, **kwargs):
        try:
            # Fetch the item by its ID and delete it
            item = Item.objects.get(pk=item_id)
            item.delete()
        except Item.DoesNotExist:
            pass  # Handle the case where the item does not exist (optional)

        return redirect('shopping_list')  # Redirect to the shopping list view


class AddItemRestView(generics.CreateAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


class RemoveItemRestView(generics.DestroyAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


class ListItemsRestView(generics.ListAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
