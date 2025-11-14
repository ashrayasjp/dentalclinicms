from django import forms

class SymptomForm(forms.Form):
    symptom_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows':5, 'placeholder':'Describe your symptoms here...'}),
        label="Symptoms",
        max_length=1000
    )
