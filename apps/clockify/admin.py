from django.contrib import admin
from .models import ClockifySettings

@admin.register(ClockifySettings)
class ClockifySettingsAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'workspace_id', 'hours_per_day')