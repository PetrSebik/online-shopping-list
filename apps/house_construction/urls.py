from django.urls import path
from .views import (
    PriorityListView,
    QAListView,
    PriorityDeleteView,
    QADeleteView,
    QAUpdateView,
    PriorityUpdateView,
)

urlpatterns = [
    path("priorities/", PriorityListView.as_view(), name="priority_list"),
    path(
        "priorities/<int:pk>/delete/",
        PriorityDeleteView.as_view(),
        name="priority_delete",
    ),
    path(
        "priorities/<int:pk>/edit/", PriorityUpdateView.as_view(), name="priority_edit"
    ),
    path("questions/", QAListView.as_view(), name="qa_list"),
    path("questions/<int:pk>/delete/", QADeleteView.as_view(), name="qa_delete"),
    path("questions/<int:pk>/edit/", QAUpdateView.as_view(), name="qa_edit"),
]
