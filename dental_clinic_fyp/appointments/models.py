# models.py
from django.db import models
from users.models import Doctor, Patient

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Reschedule Requested', 'Reschedule Requested'),
    ('Reschedule Approved', 'Reschedule Approved'),
    ('Reschedule Rejected', 'Reschedule Rejected'),
    ('Completed', 'Completed'),
]

RESCHEDULE_CHOICES = [
    ('None', 'None'),
    ('Requested', 'Requested'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
]

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateTimeField()
   
    original_date = models.DateField(blank=True, null=True)
    original_time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    patient_phone = models.CharField(max_length=15)
    payment_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Paid', 'Paid')],
        default='Pending'
    )
    reschedule_status = models.CharField(
        max_length=20,
        choices=RESCHEDULE_CHOICES,
        default='None'
    )
    proposed_date = models.DateField(null=True, blank=True)
    proposed_time = models.TimeField(null=True, blank=True)

    video_room_url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.patient} -> {self.doctor} on {self.date}"


# forms.py
from django import forms
from .models import Appointment

class RescheduleForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'notes'] 
        labels = {
            'notes': 'Reason',  # change label for display
        }# only allow rescheduling date and notes
        widgets = {
            'date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                # optional: set min to current datetime for front-end validation
                'min': '',
            }),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils import timezone
        # set min attribute dynamically to prevent past date selection in template
        now = timezone.now().strftime("%Y-%m-%dT%H:%M")
        self.fields['date'].widget.attrs['min'] = now
        
class Report(models.Model):
        appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
        doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
        patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
        signature = models.TextField( blank=True, null=True)


        blood_group = models.CharField(max_length=10)
        age = models.PositiveIntegerField(null=True, blank=True)
        gender = models.CharField(max_length=10, choices=[('Male','Male'),('Female','Female'),('Other','Other')], blank=True)

    # Dental clinical details
        diagnosis = models.TextField(blank=True)          # e.g., cavity, gingivitis
        prescription = models.TextField(blank=True)       # medicines, dental procedures
        notes = models.TextField(blank=True)              # extra observations
        vitals = models.JSONField(blank=True, null=True)  # optional, e.g., BP, pulse

    # Dental imaging
        imaging_reports = models.TextField(blank=True)   # X-rays, scans
        attachments = models.FileField(upload_to='reports/', blank=True, null=True)  # optional

    # Follow-up
        follow_up_date = models.DateField(null=True, blank=True)
        follow_up_notes = models.TextField(blank=True)

        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def __str__(self):
         return f"Report: {self.patient.user.username} - {self.appointment.date.date()}"
