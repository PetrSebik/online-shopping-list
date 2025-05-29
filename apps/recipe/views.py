from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView

from .forms import CreateRecipeForm, RecipeItemFormSet, RecipeStepFormSet
from .models import Recipe


class RecipesListView(ListView):
    template_name = 'recipes_list.html'
    queryset = Recipe.objects.prefetch_related('tags').all()
    context_object_name = 'recipes'


class RecipeDetailView(DetailView):
    template_name = 'recipes_detail.html'
    queryset = Recipe.objects.all()
    context_object_name = 'recipe'


class RecipeCreateView(CreateView):
    template_name = 'recipe_create.html'
    queryset = Recipe.objects.all()
    context_object_name = 'recipe'
    form_class = CreateRecipeForm
    success_url = reverse_lazy('recipes_list')

    def form_valid(self, form):
        # Save the Recipe instance
        recipe = form.save()

        # Process RecipeItemFormSet and RecipeStepFormSet
        item_formset = RecipeItemFormSet(self.request.POST, instance=recipe)
        step_formset = RecipeStepFormSet(self.request.POST, instance=recipe)

        print(item_formset, step_formset)
        if item_formset.is_valid() and step_formset.is_valid():
            item_formset.save()
            step_formset.save()
            return super().form_valid(form)

        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_formset'] = RecipeItemFormSet()
        context['step_formset'] = RecipeStepFormSet()
        return context
