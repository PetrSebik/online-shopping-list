from apps.clockify.models import ClockifySettings


def clockify_settings(request):
    return {
        "clockify_settings_id": ClockifySettings.objects.values_list("id", flat=True).first(),
    }
