import unicodedata
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views import View
from django.views.generic import ListView, DetailView, CreateView

from apps.shopping.models import Item
from .forms import CreateRecipeForm, RecipeItemFormSet, RecipeStepFormSet
from .models import PantryStaple, PurchaseUnit, Recipe, Tag

# Available sort orders for the recipe list. "stale" surfaces recipes that
# haven't been cooked in the longest time (never-cooked first) for meal planning.
SORT_OPTIONS = {
    "name": ["name"],
    "recent": [F("last_cooked_date").desc(nulls_last=True), "name"],
    "stale": [F("last_cooked_date").asc(nulls_first=True), "name"],
}

# "Jen dlouho nevařené" / stale-suggestions threshold: a recipe counts as
# stale once it's been this many days (or more) since it was last cooked.
STALE_THRESHOLD_DAYS = 60


def _normalize(text):
    """Lower-case and strip diacritics so "lečo" matches "leco" etc.

    SQLite has no unaccent, but the recipe set is tiny, so we filter in Python.
    """
    decomposed = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def filter_recipes(request):
    """Apply the search/tag/sort/stale GET parameters to the recipe list.

    Tags and sorting run in the DB; the (accent-insensitive) text search runs
    in Python over name + ingredient names. Returns the resulting list plus a
    dict of the parsed parameters so views can echo the filter state back to
    the controls.
    """
    qs = Recipe.objects.prefetch_related("tags", "items").distinct()

    tag_ids = [int(t) for t in request.GET.getlist("tags") if t.isdigit()]
    tag_mode = request.GET.get("tag_mode") if request.GET.get("tag_mode") in ("any", "all") else "any"
    if tag_ids:
        if tag_mode == "all":
            # Chained .filter() calls join the M2M table once per tag, so this
            # is a real AND — a single .filter(tags__in=...) can't express it.
            for tag_id in tag_ids:
                qs = qs.filter(tags=tag_id)
        else:
            qs = qs.filter(tags__in=tag_ids)

    sort = request.GET.get("sort", "name")
    order = SORT_OPTIONS.get(sort, SORT_OPTIONS["name"])
    if sort == "stale":
        # Otherwise recipes hidden from tracking (which never get a
        # last_cooked_date from the UI) would permanently sit at the top.
        qs = qs.exclude(hide_from_tracking=True)

    stale_only = request.user.is_authenticated and request.GET.get("stale_only") == "1"
    if stale_only:
        threshold = timezone.localdate() - timedelta(days=STALE_THRESHOLD_DAYS)
        qs = qs.exclude(hide_from_tracking=True).filter(
            Q(last_cooked_date__isnull=True) | Q(last_cooked_date__lte=threshold)
        )

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

    return recipes, {
        "tag_ids": tag_ids,
        "tag_mode": tag_mode,
        "query": query,
        "sort": sort,
        "stale_only": stale_only,
    }


def _stale_suggestions(limit=3):
    """The `limit` recipes longest overdue for cooking, for the list-page widget."""
    return list(
        Recipe.objects.exclude(hide_from_tracking=True)
        .order_by(F("last_cooked_date").asc(nulls_first=True), "name")[:limit]
    )


def _pantry_staple_names():
    return {n.lower() for n in PantryStaple.objects.values_list("name", flat=True)}


def _purchase_unit_names():
    return {n.lower() for n in PurchaseUnit.objects.values_list("name", flat=True)}


def _format_ingredient_line(ingredient, purchase_units):
    """Render a RecipeItem as a shopping-list line.

    A quantity is only meaningful on a shopping list if the unit is something
    you actually buy in (ks, g, kg, ml, l...) — a prep measure like "3 hrnky"
    or "2 ČL" doesn't tell you how much flour or baking soda to buy, so those
    ingredients go in by bare name only.
    """
    name = ingredient.name.strip()
    units = (ingredient.units or "").strip()
    if not ingredient.count or (units and units.lower() not in purchase_units):
        return name
    suffix = f"{ingredient.count} {units}".strip() if units else str(ingredient.count)
    return f"{name} {suffix}"


class RecipesListView(ListView):
    template_name = "recipes_list.html"
    context_object_name = "recipes"

    def get_queryset(self):
        return filter_recipes(self.request)[0]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        _, filters = filter_recipes(self.request)
        ctx["all_tags"] = Tag.objects.order_by("name")
        ctx["active_tag_ids"] = filters["tag_ids"]
        ctx["tag_mode"] = filters["tag_mode"]
        ctx["query"] = filters["query"]
        ctx["sort"] = filters["sort"]
        ctx["stale_only"] = filters["stale_only"]
        if self.request.user.is_authenticated:
            ctx["stale_suggestions"] = _stale_suggestions()
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


class AddRecipeToShoppingListView(LoginRequiredMixin, View):
    """Ingredients section has two modes, toggled in place via htmx:

    - plain (default): just the ingredient list + an "Přidat do nákupního
      seznamu" button, so it stays out of the way while cooking.
    - picker (?picker=1): the same list as a checklist (pantry staples
      pre-unchecked) with "Přidat vybrané" / "Zrušit" actions.

    POSTing the picker form adds the checked ingredients and swaps back to
    plain mode with a confirmation message.
    """

    def get(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        picker_mode = request.GET.get("picker") == "1"
        html = render_to_string(
            "recipe_ingredients_section.html",
            {
                "recipe": recipe,
                "picker_mode": picker_mode,
                "pantry_staple_names": _pantry_staple_names() if picker_mode else None,
            },
            request=request,
        )
        return HttpResponse(html)

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        item_ids = request.POST.getlist("item_ids")
        selected = recipe.items.filter(pk__in=item_ids)
        purchase_units = _purchase_unit_names()
        added = 0
        for ingredient in selected:
            line = _format_ingredient_line(ingredient, purchase_units)
            if not Item.objects.filter(name__iexact=line).exists():
                Item.objects.create(name=line)
            added += 1
        message = f"Přidáno {added} položek do nákupního seznamu." if added else "Nic nebylo vybráno."
        html = render_to_string(
            "recipe_ingredients_section.html",
            {"recipe": recipe, "picker_mode": False, "add_to_list_message": message},
            request=request,
        )
        return HttpResponse(html)


class RecipeToggleTrackingView(LoginRequiredMixin, View):
    """Flip hide_from_tracking and re-render the detail-page header (title,
    tags, cooked control, and this same toggle)."""

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe.hide_from_tracking = not recipe.hide_from_tracking
        recipe.save(update_fields=["hide_from_tracking"])
        html = render_to_string("recipe_detail_head.html", {"recipe": recipe}, request=request)
        return HttpResponse(html)


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
