from django.shortcuts import redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import DeleteView, UpdateView
from django.urls import reverse_lazy

from .forms import ConstructionQAForm, PriorityItemForm
from .models import PriorityItem, ConstructionQA


class PriorityListView(ListView):
    model = PriorityItem
    template_name = "priority_list.html"
    context_object_name = "priorities"
    ordering = ["-priority_level"]

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        PriorityItem.objects.create(
            task_name=request.POST.get("task_name"),
            description=request.POST.get("description"),
            priority_level=request.POST.get("priority_level"),
            attachment=request.FILES.get("attachment"),
        )
        return redirect("priority_list")


class PriorityDeleteView(LoginRequiredMixin, DeleteView):
    model = PriorityItem
    success_url = reverse_lazy("priority_list")


class QAListView(ListView):
    model = ConstructionQA
    template_name = "qa_list.html"
    context_object_name = "questions"
    ordering = ["-date_asked", "-id"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ConstructionQAForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        form = ConstructionQAForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect("qa_list")


class PriorityUpdateView(LoginRequiredMixin, UpdateView):
    model = PriorityItem
    form_class = PriorityItemForm
    template_name = "priority_edit.html"
    success_url = reverse_lazy("priority_list")


class QADeleteView(LoginRequiredMixin, DeleteView):
    model = ConstructionQA
    success_url = reverse_lazy("qa_list")


class QAUpdateView(LoginRequiredMixin, UpdateView):
    model = ConstructionQA
    form_class = ConstructionQAForm
    template_name = "qa_edit.html"
    success_url = reverse_lazy("qa_list")
