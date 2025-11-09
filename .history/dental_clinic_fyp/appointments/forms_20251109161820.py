from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    signature = forms.CharField(widget=forms.HiddenInput(), required=False)  # Add this field

    class Meta:
        model = Report
        fields = ['diagnosis', 'prescription', 'notes', 'imaging_reports', 'follow_up_date', 'follow_up_notes', 'signature']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows':3, 'class':'form-control'}),
            'prescription': forms.Textarea(attrs={'rows':3, 'class':'form-control'}),
            'notes': forms.Textarea(attrs={'rows':2, 'class':'form-control'}),
            'imaging_reports': forms.Textarea(attrs={'rows':2, 'class':'form-control'}),
            'follow_up_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'follow_up_notes': forms.Textarea(attrs={'rows':2, 'class':'form-control'}),
        }
