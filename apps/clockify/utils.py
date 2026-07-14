import calendar
from datetime import date, timedelta

# Red -> orange -> green, quantized into 11 discrete bands (0%, 10%, ..., 100%)
# rather than a smooth gradient, per design request.
_RED = (220, 53, 69)
_ORANGE = (253, 126, 20)
_GREEN = (25, 135, 84)
_COLOR_STEPS = 10


def _lerp_rgb(start, end, fraction):
    return tuple(round(start[i] + (end[i] - start[i]) * fraction) for i in range(3))


def quantized_progress_color(fraction):
    """Map a 0..1 fraction to one of 11 red->orange->green shades."""
    fraction = max(0.0, min(1.0, fraction))
    step = round(fraction * _COLOR_STEPS) / _COLOR_STEPS

    if step <= 0.5:
        r, g, b = _lerp_rgb(_RED, _ORANGE, step / 0.5)
    else:
        r, g, b = _lerp_rgb(_ORANGE, _GREEN, (step - 0.5) / 0.5)
    return f"rgb({r}, {g}, {b})"


def get_working_days_in_month(year, month):
    c = calendar.Calendar()
    days = c.itermonthdays2(year, month)  # (day, weekday)
    working_days = [day for day, weekday in days if day != 0 and weekday < 5]  # Mon-Fri
    return len(working_days)


def get_working_days_passed(year, month, today):
    from .models import Vacation
    c = calendar.Calendar()
    days = c.itermonthdays2(year, month)
    working_days = [
        day for day, weekday in days
        if day != 0 and weekday < 5 and day <= today.day
    ]

    start_of_month = date(year, month, 1)
    end_of_range = today

    vacations = Vacation.objects.filter(
        date_to__gte=start_of_month,
        date_from__lte=end_of_range
    )

    vacation_days = set()
    for vacation in vacations:
        vacation_start = max(vacation.date_from, start_of_month)
        vacation_end = min(vacation.date_to, end_of_range)

        if vacation_start > vacation_end:
            continue

        for i in range((vacation_end - vacation_start).days + 1):
            day = vacation_start + timedelta(days=i)
            if day.weekday() < 5:
                vacation_days.add(day.day)

    adjusted_working_days = [day for day in working_days if day not in vacation_days]
    return len(adjusted_working_days)