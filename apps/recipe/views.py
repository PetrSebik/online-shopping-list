from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView

from .forms import CreateRecipeForm, RecipeItemFormSet, RecipeStepFormSet
from .models import Recipe, Tag


class RecipesListView(ListView):
    template_name = 'recipes_list.html'
    queryset = Recipe.objects.prefetch_related('tags').all()
    context_object_name = 'recipes'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        active_tag_ids = set()
        all_tags = Tag.objects.all().order_by("name")
        for t in all_tags:
            t.is_active = True
            active_tag_ids.add(t.id)

        ctx["all_tags"] = all_tags
        ctx["active_tag_ids"] = active_tag_ids
        return ctx


class RecipesListFilteredView(ListView):
    template_name = 'recipes_list_partial.html'
    queryset = Recipe.objects.prefetch_related('tags').all()
    context_object_name = 'recipes'

    def get_tag_ids(self) -> list[int]:
        """
        Parse 'tags' GET parameter into a list of integers.
        Ignores empty strings or invalid integers.
        """
        tags_param = self.request.GET.get('tags', '')
        return [int(t.strip()) for t in tags_param.split(',') if t.strip().isdigit()]

    def get_queryset(self):
        qs = Recipe.objects.prefetch_related('tags')
        tag_ids = self.get_tag_ids()
        if tag_ids:
            qs = qs.filter(tags__in=tag_ids).distinct()
        elif len(tag_ids) == 0:
            qs = qs.none()
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        active_tag_ids = self.get_tag_ids()
        all_tags = Tag.objects.all().order_by("name")
        for t in all_tags:
            t.is_active = t.id in active_tag_ids

        ctx["all_tags"] = all_tags
        ctx["active_tag_ids"] = active_tag_ids
        return ctx


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
