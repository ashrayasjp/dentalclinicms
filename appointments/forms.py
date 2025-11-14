from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    signature = forms.CharField(widget=forms.HiddenInput(), required=False)

    follow_up_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control'}
        ),
        input_formats=['%Y-%m-%dT%H:%M']  # <-- THIS IS REQUIRED
    )

    class Meta:
        model = Report
        fields = [
            'diagnosis', 'prescription', 'notes',
            'imaging_reports', 'follow_up_date',
            'follow_up_notes', 'signature'
        ]

        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows':3, 'class':'form-control'}),
            'prescription': forms.Textarea(attrs={'rows':3, 'class':'form-control'}),
            'notes': forms.Textarea(attrs={'rows':2, 'class':'form-control'}),
            'imaging_reports': forms.Textarea(attrs={'rows':2, 'class':'form-control'}),
            'follow_up_notes': forms.Textarea(attrs={'rows':2, 'class':'form-control'}),
            'signature': forms.HiddenInput(),
        }
