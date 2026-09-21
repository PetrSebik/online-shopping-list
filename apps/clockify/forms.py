from datetime import date

from django import forms

from .models import HourAdjustment


class HourAdjustmentForm(forms.ModelForm):
    class Meta:
        model = HourAdjustment
        fields = ["date", "hours", "note"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "hours": forms.NumberInput(attrs={
                "step": "0.25", "min": "0.25", "class": "form-control", "placeholder": "e.g. 5",
            }),
            "note": forms.TextInput(attrs={"class": "form-control", "placeholder": "optional"}),
        }

    def clean_date(self):
        value = self.cleaned_data["date"]
        today = date.today()
        if value > today:
            raise forms.ValidationError("Date can't be in the future.")
        if value.year != today.year or value.month != today.month:
            raise forms.ValidationError("Date must be in the current month.")
        return value

    def clean_hours(self):
        value = self.cleaned_data["hours"]
        if value <= 0:
            raise forms.ValidationError("Hours must be greater than zero.")
        return value
