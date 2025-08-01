import calendar
from decimal import Decimal

import requests
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.generic import TemplateView

from .models import ClockifySettings, Vacation
from .utils import get_working_days_in_month, get_working_days_passed


class ClockifyMonthlySummaryView(TemplateView):
    template_name = "clockify.html"

    @staticmethod
    def format_hours_minutes(hours_decimal: float) -> str:
        total_minutes = round(hours_decimal * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours}h {minutes}m"

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get("uuid")
        clockify_setting = get_object_or_404(ClockifySettings, pk=uuid)
        if not clockify_setting:
            return self.render_to_response({"error": "Clockify settings not configured."})

        today = now().date()
        year, month = today.year, today.month

        total_working_days = get_working_days_in_month(year, month)
        working_days_passed = get_working_days_passed(year, month, today)

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
                "ids": [clockify_setting.user_id],
                "status": "ACTIVE_WITH_PENDING",
                "numberOfDeleted": 0
            },
            "summaryFilter": {
                "sortColumn": "GROUP",
                "groups": ["PROJECT", "TIMEENTRY"]
            }
        }

        url = f"https://reports.api.clockify.me/v1/workspaces/{clockify_setting.workspace_id}/reports/summary"
        headers = {
            "X-Api-Key": clockify_setting.api_key,
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=request_body)

        if response.status_code != 200:
            return self.render_to_response({"error": "Failed to fetch summary report from Clockify API."})

        data = response.json()

        # Extract totalTime in seconds
        total_seconds = data.get("totals", [{}])[0].get("totalTime", 0)
        total_hours = Decimal(total_seconds) / Decimal(3600)

        plan_hours_passed = clockify_setting.hours_per_day_plan * working_days_passed
        total_plan_hours = clockify_setting.total_hours_plan
        diff_hours = total_hours - plan_hours_passed

        context = {
            "total_hours": self.format_hours_minutes(total_hours),
            "plan_hours_passed": self.format_hours_minutes(plan_hours_passed),
            "hours_per_day_plan": self.format_hours_minutes(clockify_setting.hours_per_day_plan),
            "total_plan_hours": self.format_hours_minutes(total_plan_hours),
            "diff_hours": self.format_hours_minutes(abs(diff_hours)),
            "behind": diff_hours < 0,
            "ahead": diff_hours > 0,
            "working_days_passed": working_days_passed,
            "total_working_days": Vacation.working_days_this_month(),
            "vacations_days": Vacation.working_vacation_days_in_month()
        }
        return self.render_to_response(context)
