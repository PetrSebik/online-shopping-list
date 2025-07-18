from django.urls import path
from .views import (
    ClockifyMonthlySummaryView
)

urlpatterns = [
    path("reports/<uuid:uuid>/", ClockifyMonthlySummaryView.as_view(), name="clockify-report"),
]
