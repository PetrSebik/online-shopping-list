from django import template
from django.utils import timezone

register = template.Library()


def _days(value):
    if not value:
        return None
    return (timezone.localdate() - value).days


@register.filter
def cooked_since(value):
    """Human, Czech relative label for a last-cooked date."""
    d = _days(value)
    if d is None:
        return "Zatím nevařeno"
    if d < 0:
        return "Naplánováno"
    if d == 0:
        return "Vařeno dnes"
    if d == 1:
        return "Vařeno včera"
    if d < 31:
        return f"Před {d} dny"
    months = d // 30
    if months == 1:
        return "Před měsícem"
    if months < 12:
        return f"Před {months} měsíci"
    years = d // 365
    if years == 1:
        return "Před rokem"
    return f"Před {years} lety"


@register.filter
def cooked_freshness(value):
    """Bucket used to colour the freshness rail/dot."""
    d = _days(value)
    if d is None:
        return "never"
    if d <= 14:
        return "fresh"
    if d <= 45:
        return "recent"
    if d <= 120:
        return "aging"
    return "stale"


@register.filter
def recipe_count_cs(n):
    """Grammatically correct Czech count: 1 recept / 2 recepty / 5 receptů."""
    n = int(n)
    if n == 1:
        return "1 recept"
    if 2 <= n <= 4:
        return f"{n} recepty"
    return f"{n} receptů"
