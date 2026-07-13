import calendar
from decimal import Decimal

import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.generic import TemplateView

from .models import ClockifySettings, Vacation
from .utils import get_working_days_in_month, get_working_days_passed


class ClockifyMonthlySummaryView(LoginRequiredMixin, TemplateView):
    template_name = "clockify.html"

    @staticmethod
    def format_hours_minutes(hours_decimal: float) -> str:
        total_minutes = round(hours_decimal * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if minutes == 0:
            return f"{hours}h"
        return f"{hours}h {minutes}m"

    @staticmethod
    def fetch_total_hours(clockify_setting, date_from_iso, date_to_iso):
        request_body = {
            "dateRangeStart": date_from_iso,
            "dateRangeEnd": date_to_iso,
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
            return None

        data = response.json()
        total_seconds = data.get("totals", [{}])[0].get("totalTime", 0)
        return Decimal(total_seconds) / Decimal(3600)

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get("uuid")
        clockify_setting = get_object_or_404(ClockifySettings, pk=uuid)
        if not clockify_setting:
            return self.render_to_response({"error": "Clockify settings not configured."})

        today = now().date()
        year, month = today.year, today.month

        total_working_days = get_working_days_in_month(year, month)
        working_days_passed = get_working_days_passed(year, month, today)

        total_hours = self.fetch_total_hours(
            clockify_setting,
            f"{year}-{month:02d}-01T00:00:00.000Z",
            f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}T23:59:59.999Z",
        )
        if total_hours is None:
            return self.render_to_response({"error": "Failed to fetch summary report from Clockify API."})

        today_iso = today.isoformat()
        today_hours = self.fetch_total_hours(
            clockify_setting,
            f"{today_iso}T00:00:00.000Z",
            f"{today_iso}T23:59:59.999Z",
        ) or Decimal(0)

        is_vacation_today = Vacation.objects.filter(date_from__lte=today, date_to__gte=today).exists()
        is_working_day_today = today.weekday() < 5 and not is_vacation_today

        plan_hours_passed = clockify_setting.hours_per_day_plan * working_days_passed
        total_plan_hours = clockify_setting.total_hours_plan
        diff_hours = total_hours - plan_hours_passed
        total_working_days = Vacation.working_days_this_month()

        percent_days_passed = round(working_days_passed / total_working_days * 100) if total_working_days else 0
        percent_hours_done = round(float(total_hours) / float(total_plan_hours) * 100) if total_plan_hours else 0

        remaining_working_days = max(total_working_days - working_days_passed, 0)
        remaining_hours = total_plan_hours - total_hours
        target_met = remaining_hours <= 0

        if remaining_working_days > 0 and not target_met:
            required_hours_per_day = remaining_hours / remaining_working_days
        else:
            required_hours_per_day = Decimal(0)

        # Daily bar tracks against the catch-up pace, falling back to the flat plan
        # once there's no gap left to close (target already met, or no days left to spread it over).
        daily_target_is_catchup = required_hours_per_day > 0
        daily_target = required_hours_per_day if daily_target_is_catchup else clockify_setting.hours_per_day_plan
        diff_today = today_hours - daily_target
        percent_today = round(float(today_hours) / float(daily_target) * 100) if daily_target else 0

        if working_days_passed > 0:
            projected_total_hours = (total_hours / working_days_passed) * total_working_days
        else:
            projected_total_hours = Decimal(0)
        projected_diff = projected_total_hours - total_plan_hours

        projected_earnings = None
        if clockify_setting.hour_rate:
            projected_earnings = f"{round(projected_total_hours * clockify_setting.hour_rate):,}".replace(",", " ")

        context = {
            "month_label": today.strftime("%B %Y"),
            "is_working_day_today": is_working_day_today,
            "today_hours": self.format_hours_minutes(today_hours),
            "daily_target": self.format_hours_minutes(daily_target),
            "daily_target_is_catchup": daily_target_is_catchup,
            "percent_today": percent_today,
            "percent_today_bar": min(percent_today, 100),
            "today_behind": diff_today < 0,
            "today_ahead": diff_today > 0,
            "total_hours": self.format_hours_minutes(total_hours),
            "plan_hours_passed": self.format_hours_minutes(plan_hours_passed),
            "hours_per_day_plan": self.format_hours_minutes(clockify_setting.hours_per_day_plan),
            "total_plan_hours": self.format_hours_minutes(total_plan_hours),
            "diff_hours": self.format_hours_minutes(abs(diff_hours)),
            "behind": diff_hours < 0,
            "ahead": diff_hours > 0,
            "working_days_passed": working_days_passed,
            "total_working_days": total_working_days,
            "vacations_days": Vacation.working_vacation_days_in_month(),
            "percent_days_passed": percent_days_passed,
            "percent_hours_done": percent_hours_done,
            "percent_hours_done_bar": min(percent_hours_done, 100),
            "remaining_working_days": remaining_working_days,
            "target_met": target_met,
            "required_hours_per_day": self.format_hours_minutes(required_hours_per_day),
            "projected_total_hours": self.format_hours_minutes(projected_total_hours),
            "projected_diff": self.format_hours_minutes(abs(projected_diff)),
            "projected_ahead": projected_diff > 0,
            "projected_behind": projected_diff < 0,
            "projected_earnings": projected_earnings,
        }
        return self.render_to_response(context)
