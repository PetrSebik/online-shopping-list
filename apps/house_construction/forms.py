from django import forms
from .models import ConstructionQA

class ConstructionQAForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap classes to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = ConstructionQA
        fields = ['question', 'answer']
        widgets = {
            'question': forms.TextInput(attrs={'placeholder': 'Zadejte vaši otázku...'}),
            'answer': forms.Textarea(attrs={'placeholder': 'Zde dopište odpověď...', 'rows': 4}),
        }