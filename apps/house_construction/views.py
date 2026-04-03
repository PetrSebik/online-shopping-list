from django.db import transaction
from django.shortcuts import redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import DeleteView, UpdateView
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView
from django.http import Http404
from .models import ProjectImage, AdditionalImage
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

from .forms import ConstructionQAForm, PriorityItemForm, ProjectImageForm
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

    def get_queryset(self):
        queryset = super().get_queryset()

        # Check if the user is logged in
        if self.request.user.is_authenticated:
            return queryset
        else:
            return queryset.filter(hide=False)


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


class MediaListView(ListView):
    model = ProjectImage
    template_name = "media_list.html"
    context_object_name = "images"
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            return queryset
        return queryset.filter(hide=False)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        title = request.POST.get("title")
        description = request.POST.get("description")
        image_file = request.FILES.get("image")
        is_hidden = request.POST.get("hide") == "on"

        if image_file:
            try:
                with transaction.atomic():
                    new_photo = ProjectImage(
                        title=title,
                        description=description,
                        image=image_file,
                        hide=is_hidden,
                    )

                    img = Image.open(image_file)
                    original_format = img.format if img.format else "JPEG"

                    img.thumbnail((400, 300))

                    thumb_io = BytesIO()
                    img.save(thumb_io, format=original_format, quality=85)

                    thumb_filename = f"thumb_{image_file.name}"
                    new_photo.thumbnail.save(
                        thumb_filename, ContentFile(thumb_io.getvalue()), save=False
                    )

                    new_photo.save()

                    extra_files = request.FILES.getlist("extra_images")
                    for f in extra_files:
                        AdditionalImage.objects.create(project_image=new_photo, image=f)

            except Exception as e:
                # You could add a message here for debugging on the Pi
                print(f"Error saving gallery: {e}")

        return redirect("media_list")


class MediaDetailView(DetailView):
    model = ProjectImage
    template_name = "media_detail.html"
    context_object_name = "image"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.hide and not self.request.user.is_authenticated:
            raise Http404("Fotografie nebyla nalezena.")
        return obj


class MediaUpdateView(LoginRequiredMixin, UpdateView):
    model = ProjectImage
    form_class = ProjectImageForm
    template_name = "media_edit.html"

    def get_success_url(self):
        return reverse_lazy("media_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        if "image" in form.changed_data:
            image_file = form.cleaned_data["image"]
            img = Image.open(image_file)

            original_format = img.format if img.format else "JPEG"
            img.thumbnail((400, 300))

            thumb_io = BytesIO()
            img.save(thumb_io, format=original_format, quality=85)

            thumb_filename = f"thumb_{image_file.name}"
            self.object.thumbnail.save(
                thumb_filename, ContentFile(thumb_io.getvalue()), save=False
            )

        response = super().form_valid(form)
        extra_files = self.request.FILES.getlist("extra_images")

        if extra_files:
            from django.db import transaction

            with transaction.atomic():
                for f in extra_files:
                    AdditionalImage.objects.create(project_image=self.object, image=f)

        return response


class MediaDeleteView(LoginRequiredMixin, DeleteView):
    model = ProjectImage
    success_url = reverse_lazy("media_list")


class AdditionalImageDeleteView(LoginRequiredMixin, DeleteView):
    model = AdditionalImage

    def get_success_url(self):
        project_id = self.object.project_image.id
        return reverse("media_edit", kwargs={"pk": project_id})

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
