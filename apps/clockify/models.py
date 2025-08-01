import uuid
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from django.db import models


class ClockifySettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_key = models.CharField(max_length=100)
    workspace_id = models.CharField(max_length=50)
    user_id = models.CharField(max_length=50)
    hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    total_hours = models.IntegerField(null=True, blank=True)

    @property
    def hours_per_day_plan(self) -> Decimal:
        if self.hours_per_day:
            return self.hours_per_day
        elif self.total_hours:
            return Decimal(self.total_hours / Vacation.working_days_this_month())
        else:
            return Decimal(0)

    @property
    def total_hours_plan(self) -> Decimal:
        if self.total_hours:
            return Decimal(self.total_hours)
        elif self.hours_per_day:
            return Decimal(self.hours_per_day * Vacation.working_days_this_month())
        else:
            return Decimal(0)

    def __str__(self):
        return f"Clockify Settings {self.id} for user {self.user_id}"


class Vacation(models.Model):
    date_from = models.DateField()
    date_to = models.DateField()

    @classmethod
    def working_vacation_days_in_month(cls, year=None, month=None):
        today = date.today()
        year = year or today.year
        month = month or today.month

        start_of_month = date(year, month, 1)
        end_of_month = date(year, month, monthrange(year, month)[1])

        vacations = cls.objects.filter(
            date_to__gte=start_of_month,
            date_from__lte=end_of_month
        )

        total_vacation_days = 0
        for vacation in vacations:
            vacation_start = max(vacation.date_from, start_of_month)
            vacation_end = min(vacation.date_to, end_of_month)

            if vacation_start > vacation_end:
                continue

            total_vacation_days += sum(
                1 for i in range((vacation_end - vacation_start).days + 1)
                if (vacation_start + timedelta(days=i)).weekday() < 5
            )

        return total_vacation_days

    @classmethod
    def working_days_this_month(cls):
        today = date.today()
        year = today.year
        month = today.month
        start_of_month = date(year, month, 1)
        end_of_month = date(year, month, monthrange(year, month)[1])

        total_working_days = sum(
            1 for i in range((end_of_month - start_of_month).days + 1)
            if (start_of_month + timedelta(days=i)).weekday() < 5
        )
        return total_working_days - cls.working_vacation_days_in_month()
