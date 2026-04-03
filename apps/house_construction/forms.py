from django import forms
from .models import ConstructionQA, PriorityItem, ProjectImage


class ConstructionQAForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap classes to all fields
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    class Meta:
        model = ConstructionQA
        fields = ["question", "answer"]
        widgets = {
            "question": forms.TextInput(
                attrs={"placeholder": "Zadejte vaši otázku..."}
            ),
            "answer": forms.Textarea(
                attrs={"placeholder": "Zde dopište odpověď...", "rows": 4}
            ),
        }


class PriorityItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    class Meta:
        model = PriorityItem
        fields = ["task_name", "description", "priority_level", "attachment", "hide"]
        widgets = {
            "hide": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultiFileInput(attrs={"multiple": True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProjectImageForm(forms.ModelForm):
    extra_images = MultipleFileField(
        widget=MultiFileInput(
            attrs={"multiple": True, "class": "form-control", "accept": "image/*"}
        ),
        required=False,
        label="Přidat další fotografie",
    )

    class Meta:
        model = ProjectImage
        fields = ["title", "description", "image", "hide"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "image": forms.FileInput(
                attrs={"class": "form-control"}
            ),  # Single file for main
            "hide": forms.CheckboxInput(
                attrs={"class": "form-check-input", "role": "switch"}
            ),
        }
