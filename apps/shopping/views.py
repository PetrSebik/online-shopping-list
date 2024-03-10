from django.shortcuts import redirect
from django.views import View
from django.views.generic.edit import FormView, ModelFormMixin
from django.views.generic import TemplateView, ListView, CreateView
from rest_framework import generics, status
from rest_framework.response import Response
from .forms import AddItemForm, HtmxItemForm
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

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_200_OK)


class ListItemsRestView(generics.ListAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


class HTMXShoppingBaseView(TemplateView):
    template_name = 'htmx/shopping.html'


class HTMXShoppingListView(ListView):
    queryset = Item.objects.all()
    template_name = 'htmx/list_item.html'
    context_object_name = 'shopping_items'


class HTMXShoppingAddItemView(ModelFormMixin, TemplateView):
    queryset = Item.objects.all()
    template_name = 'htmx/item.html'
    context_object_name = 'item'
    form_class = HtmxItemForm
    allowed_methods = ['get', 'post',]

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            context = {"item": form.instance}
            return self.render_to_response(context)
