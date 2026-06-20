import unicodedata

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.dateparse import parse_date
from django.views import View
from django.views.generic import ListView, DetailView, CreateView

from .forms import CreateRecipeForm, RecipeItemFormSet, RecipeStepFormSet
from .models import Recipe, Tag

# Available sort orders for the recipe list. "stale" surfaces recipes that
# haven't been cooked in the longest time (never-cooked first) for meal planning.
SORT_OPTIONS = {
    "name": ["name"],
    "recent": [F("last_cooked_date").desc(nulls_last=True), "name"],
    "stale": [F("last_cooked_date").asc(nulls_first=True), "name"],
}


def _normalize(text):
    """Lower-case and strip diacritics so "lečo" matches "leco" etc.

    SQLite has no unaccent, but the recipe set is tiny, so we filter in Python.
    """
    decomposed = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def filter_recipes(request):
    """Apply the search/tag/sort GET parameters to the recipe list.

    Tags and sorting run in the DB; the (accent-insensitive) text search runs
    in Python over name + ingredient names. Returns the resulting list plus the
    parsed parameters so views can echo the filter state back to the controls.
    """
    qs = Recipe.objects.prefetch_related("tags", "items").distinct()

    tag_ids = [int(t) for t in request.GET.getlist("tags") if t.isdigit()]
    if tag_ids:
        # OR logic: a recipe matches if it has ANY of the selected tags.
        qs = qs.filter(tags__in=tag_ids)

    sort = request.GET.get("sort", "name")
    order = SORT_OPTIONS.get(sort, SORT_OPTIONS["name"])
    recipes = list(qs.order_by(*order))

    query = request.GET.get("q", "").strip()
    if query:
        needle = _normalize(query)
        recipes = [
            r for r in recipes
            if needle in _normalize(r.name)
            or any(needle in _normalize(i.name) for i in r.items.all())
            or any(needle in _normalize(t.name) for t in r.tags.all())
        ]

    return recipes, tag_ids, query, sort


class RecipesListView(ListView):
    template_name = "recipes_list.html"
    context_object_name = "recipes"

    def get_queryset(self):
        return filter_recipes(self.request)[0]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        _, tag_ids, query, sort = filter_recipes(self.request)
        ctx["all_tags"] = Tag.objects.order_by("name")
        ctx["active_tag_ids"] = tag_ids
        ctx["query"] = query
        ctx["sort"] = sort
        return ctx


class RecipesListFilteredView(ListView):
    """htmx endpoint that returns just the list of recipe cards."""
    template_name = "recipes_list_partial.html"
    context_object_name = "recipes"

    def get_queryset(self):
        return filter_recipes(self.request)[0]


class RecipeDetailView(DetailView):
    template_name = "recipes_detail.html"
    queryset = Recipe.objects.all()
    context_object_name = "recipe"


class RecipeCookedView(LoginRequiredMixin, View):
    """Set (or clear) a recipe's last cooked date and return the updated control.

    Signed-in only, since the site is public on the internet.
    """

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe.last_cooked_date = parse_date(request.POST.get("last_cooked_date", ""))
        recipe.save(update_fields=["last_cooked_date"])
        html = render_to_string(
            "recipe_cooked_control.html", {"recipe": recipe}, request=request
        )
        return HttpResponse(html)


class RecipeCreateView(LoginRequiredMixin, CreateView):
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
