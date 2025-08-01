from django.contrib import admin

from .models import ClockifySettings, Vacation


@admin.register(ClockifySettings)
class ClockifySettingsAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'workspace_id', 'hours_per_day')


@admin.register(Vacation)
class VacationAdmin(admin.ModelAdmin):
    list_display = ('date_from', 'date_to')
