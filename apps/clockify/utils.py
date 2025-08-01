import calendar
from datetime import date, timedelta

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