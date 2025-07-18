from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.utils.timezone import now
import requests
from decimal import Decimal
import calendar

from .models import ClockifySettings

class ClockifyMonthlySummaryView(TemplateView):
    template_name = "clockify.html"

    def get_working_days_in_month(self, year, month):
        c = calendar.Calendar()
        days = c.itermonthdays2(year, month)  # (day, weekday)
        working_days = [day for day, weekday in days if day != 0 and weekday < 5]  # Mon-Fri
        return len(working_days)

    def get_working_days_passed(self, year, month, today):
        c = calendar.Calendar()
        days = c.itermonthdays2(year, month)
        working_days = [day for day, weekday in days if day != 0 and weekday < 5 and day <= today.day]
        return len(working_days)

    @staticmethod
    def format_hours_minutes(hours_decimal: float) -> str:
        total_minutes = round(hours_decimal * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours}h {minutes}m"

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get("uuid")
        settings = get_object_or_404(ClockifySettings, pk=uuid)
        if not settings:
            return self.render_to_response({"error": "Clockify settings not configured."})

        today = now().date()
        year, month = today.year, today.month

        total_working_days = self.get_working_days_in_month(year, month)
        working_days_passed = self.get_working_days_passed(year, month, today)

        # Prepare the request body exactly as you use it for the summary API
        request_body = {
            "dateRangeStart": f"{year}-{month:02d}-01T00:00:00.000Z",
            "dateRangeEnd": f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}T23:59:59.999Z",
            "sortOrder": "ASCENDING",
            "rounding": True,
            "amounts": [],
            "zoomLevel": "MONTH",
            "users": {
                "contains": "CONTAINS",
                "ids": [settings.user_id],
                "status": "ACTIVE_WITH_PENDING",
                "numberOfDeleted": 0
            },
            "summaryFilter": {
                "sortColumn": "GROUP",
                "groups": ["PROJECT", "TIMEENTRY"]
            }
        }

        url = f"https://reports.api.clockify.me/v1/workspaces/{settings.workspace_id}/reports/summary"
        headers = {
            "X-Api-Key": settings.api_key,
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=request_body)

        if response.status_code != 200:
            return self.render_to_response({"error": "Failed to fetch summary report from Clockify API."})

        data = response.json()

        # Extract totalTime in seconds
        total_seconds = data.get("totals", [{}])[0].get("totalTime", 0)
        total_hours = Decimal(total_seconds) / Decimal(3600)

        plan_hours_passed = settings.hours_per_day * working_days_passed
        total_plan_hours = settings.hours_per_day * total_working_days
        diff_hours = total_hours - plan_hours_passed

        context = {
            "total_hours": self.format_hours_minutes(total_hours),
            "plan_hours_passed": self.format_hours_minutes(plan_hours_passed),
            "total_plan_hours": self.format_hours_minutes(total_plan_hours),
            "diff_hours": self.format_hours_minutes(abs(diff_hours)),
            "behind": diff_hours < 0,
            "ahead": diff_hours > 0,
            "working_days_passed": working_days_passed,
            "total_working_days": total_working_days,
        }
        return self.render_to_response(context)
