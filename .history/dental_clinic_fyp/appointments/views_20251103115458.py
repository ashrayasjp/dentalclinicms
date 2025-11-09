from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Appointment
from users.models import Doctor, Patient
from django.http import HttpResponse
from users.models import Doctor
from datetime import datetime
from django.urls import reverse
import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Appointment

from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Appointment, Doctor, Patient
from dotenv import load_dotenv
import os
from django.views.decorators.csrf import csrf_protect  
from .models import RescheduleForm
# Correct import
from .forms import ReportForm


DAILY_API_KEY = os.getenv("DAILY_API_KEY")
DAILY_API_URL = "https://api.daily.co/v1/rooms"

from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Appointment
from users.models import Doctor, Patient
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Appointment, Doctor, Patient

@login_required
def create_appointment(request):
    doctors = Doctor.objects.filter(user__is_approved=True)
    patient, _ = Patient.objects.get_or_create(user=request.user)
    now = timezone.now()

    # Automatically mark past appointments as completed
    Appointment.objects.filter(patient=patient, status='Pending', date__lt=now).update(status='Completed')

    # Compute total appointments and next appointment for dashboard
    total_appointments = Appointment.objects.filter(patient=patient).count()
    today = timezone.localdate()
    next_appointment = Appointment.objects.filter(
        patient=patient,
        date__date__gte=today
    ).order_by('date').first()

    if request.method == 'POST':
        # Prevent booking if any active future appointment exists
        active_appointment = Appointment.objects.filter(
            patient=patient,
            status__in=['Pending', 'Reschedule Approved','Reschedule Requested'],
            date__gte=now
        ).exists()  # Use exists() instead of first()

        if active_appointment:
            messages.error(request, "You already have an active appointment. Complete it before booking a new one.")
            return render(request, 'appointments/dashboard_patient.html', {
                'doctors': doctors,
                'patient_age': patient.age,
                'patient_gender': patient.gender,
                'total_appointments': total_appointments,
                'next_appointment': next_appointment
            })

        doctor_id = request.POST.get('doctor')
        date_input = request.POST['date']
        time_input = request.POST['time']
        notes = request.POST.get('notes', '')

        doctor = get_object_or_404(Doctor, id=doctor_id)

        # Combine date and time
        appointment_naive = datetime.strptime(f"{date_input} {time_input}", "%Y-%m-%d %H:%M")
        appointment_datetime = timezone.make_aware(appointment_naive)

        # Prevent booking in the past
        if appointment_datetime < now:
            messages.error(request, "You cannot select a past date/time for an appointment.")
            return render(request, 'appointments/dashboard_patient.html', {
                'doctors': doctors,
                'patient_age': patient.age,
                'patient_gender': patient.gender,
                'total_appointments': total_appointments,
                'next_appointment': next_appointment
            })

        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=appointment_datetime,
            notes=notes,
            status='Pending',
            payment_status='Pending'
        )

        messages.success(request, "Appointment booked successfully!")
        return redirect('appointments:appointment_list')

    return render(request, 'appointments/dashboard_patient.html', {
        'doctors': doctors,
        'patient_age': patient.age,
        'patient_gender': patient.gender,
        'total_appointments': total_appointments,
        'next_appointment': next_appointment
    })

from django.shortcuts import render
from .models import Report  # assuming your report model is named Report

@login_required
def report_list(request):
    # Get reports for the logged-in patient
    reports = Report.objects.filter(patient=request.user.patient).order_by('-created_at')
    context = {
        'reports': reports
    }
    return render(request, 'appointments/report_list.html', context)

# Admin-only decorator
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'admin')(view_func)

from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import Doctor, Patient
from .models import Appointment



from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Appointment, Patient

@login_required
def appointment_list(request):
    if request.user.role != 'patient':
        return redirect('/')

    patient, _ = Patient.objects.get_or_create(user=request.user)
    now = timezone.now()

    # --- Auto-cancel overdue appointments (24+ hours past scheduled time) ---
    overdue_appointments = Appointment.objects.filter(
        patient=patient,
        date__lt=now - timedelta(hours=24)
    ).exclude(status__in=["Completed", "Cancelled"])

    for appt in overdue_appointments:
        appt.status = "Cancelled"
        appt.save()

    # --- Separate appointments into pending and completed sets ---
    pending_appointments = Appointment.objects.filter(
        patient=patient,
        status__in=["Pending", "Reschedule Requested", "Reschedule Approved", "Reschedule Rejected"]
    ).order_by('-date')

    completed_appointments = Appointment.objects.filter(
        patient=patient,
        status__in=["Completed", "Cancelled"]
    ).order_by('-date')

    # --- Add dynamic reschedule labels for pending ones ---
    for appt in pending_appointments:
        if appt.status == "Reschedule Requested":
            appt.reschedule_label = "Requested"
            appt.reschedule_class = "btn btn-sm"
            appt.reschedule_style = "background-color: #dce6f7; color: #000;"
        elif appt.status == "Reschedule Approved":
            appt.reschedule_label = "Approved"
            appt.reschedule_class = "btn btn-sm btn-success"
            appt.reschedule_style = ""
        elif appt.status == "Reschedule Rejected":
            appt.reschedule_label = "Rejected"
            appt.reschedule_class = "btn btn-sm btn-danger"
            appt.reschedule_style = ""
        else:
            appt.reschedule_label = None  # Shows Reschedule button

    context = {
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
    }

    return render(request, 'appointments/appointment_list.html', context)


# Doctor: View only their appointments




# Separate view for doctor to see their appointments
@login_required
def doctor_appointments(request):
    if request.user.role != 'doctor':
        return redirect('/')

    appointments = Appointment.objects.filter(doctor=request.user.doctor).order_by('-date')

    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments,
        'is_doctor': True
    })

# Appointment detail
@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    return render(request, 'appointments/appointment_detail.html', {'appointment': appointment})

# Admin: Approve/cancel
@admin_required
def approve_appointments(request):
    appointments = Appointment.objects.filter(status='Pending')
    if request.method == 'POST':
        appt_id = request.POST.get('appointment_id')
        action = request.POST.get('action')
        appt = get_object_or_404(Appointment, id=appt_id)
        if action == 'approve':
            appt.status = 'Approved'
        else:
            appt.status = 'Cancelled'
        appt.save()
    return render(request, 'appointments/approve_appointments.html', {'appointments': appointments})


@login_required
def edit_appointment(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)

    # Only the patient who booked can edit
    if request.user.role != 'patient' or appointment.patient.user != request.user:
        return redirect('appointments:appointment_list')

    if request.method == 'POST':
        appointment.date = request.POST.get('date')
        appointment.notes = request.POST.get('notes', '')
        appointment.save()
        messages.success(request, "Appointment updated successfully!")
        return redirect('appointments:appointment_list')

    return render(request, 'appointments/edit_appointment.html', {'appointment': appointment})

# views.py
@login_required
def pay_esewa_redirect(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        patient_phone = request.POST.get("phone")  # From your payment form

        # Generate unique transaction ID
        pid = str(uuid.uuid4())

        esewa_data = {
            'amt': 1000,  # amount
            'tAmt': 1000, # total amount
            'txAmt': 0, 
            'phone': patient_phone,
            'psc': 0,
            'pdc': 0,
            'pid': pid,
            'scd': 'EPAYTEST',  # sandbox merchant code
            'su': 'https://uncharmed-poetastrical-bill.ngrok-free.dev/appointments/payment/success/',
            'fu': 'https://uncharmed-poetastrical-bill.ngrok-free.dev/appointments/payment/failure/',
            'receiver': '9823588827',  # your clinic receiver
            'patient_phone': patient_phone,
        }

        return render(request, 'appointments/esewa_redirect.html', {'esewa_data': esewa_data})

    return redirect('appointments:appointment_list')

@login_required
def esewa_success(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    # Mark appointment as paid
    appointment.payment_status = 'Paid'
    appointment.save()
    messages.success(request, "Payment completed successfully!")
    return redirect('appointments:appointment_list')


@login_required
def esewa_failure(request, appointment_id):
    messages.error(request, "Payment failed or cancelled.")
    return redirect('appointments:appointment_list')

@login_required
def dashboard_patient(request):
     doctors = Doctor.objects.all().order_by('user__username')
     appointments = Appointment.objects.filter(patient=request.user.patient).order_by('-date')
     return render(request, 'appointments/dashboard_patient.html', {
        'appointments': appointments,
        'doctors': doctors
    })

@login_required
def esewa_payment_page(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        if len(phone) != 10 or not phone.isdigit() or not phone.startswith('9'):
            messages.error(request, "Enter a valid 10-digit Nepali phone number starting with 9")
            return redirect('appointments:esewa_payment_page', appointment_id=appointment.id)

        appointment.patient_phone = phone
        appointment.save()

        esewa_data = {
            'amt': 1000,
            'tAmt': 1000,
            'txAmt': 0,
            'psc': 0,
            'pdc': 0,
            'pid': appointment.id,
            'scd': 'EPAYTEST',
            'su': request.build_absolute_uri(reverse('appointments:esewa_success', args=[appointment.id])),
            'fu': request.build_absolute_uri(reverse('appointments:esewa_failure', args=[appointment.id])),
            'receiver': '9823588827',
        }

        return render(request, 'appointments/esewa_redirect.html', {'esewa_data': esewa_data})

    return render(request, 'appointments/esewa_payment_page.html', {'appointment': appointment})



@login_required
def mock_payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        
        # Check phone validity: must be 10 digits starting with 9
        if len(phone) != 10 or not phone.isdigit() or not phone.startswith('9'):
            messages.error(request, "Enter a valid 10-digit Nepali phone number starting with 9")
            return redirect('appointments:mock_payment', appointment_id=appointment.id)

        # Mark payment as done
        appointment.payment_status = 'Paid'
        appointment.patient_phone = phone
        appointment.save()

        messages.success(request, "Mock payment successful!")
        return redirect('appointments:appointment_list')  # Redirect to appointment list

    return render(request, 'appointments/mock_payment.html', {'appointment': appointment})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
import requests

@login_required
@csrf_protect
def start_video_call(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    user = request.user

    # Verify ownership
    if user.role == 'doctor' and appointment.doctor.user != user:
        return redirect('unauthorized')
    if user.role == 'patient' and appointment.patient.user != user:
        return redirect('unauthorized')

    # Create Daily.co room if not exists
    if not appointment.video_room_url:
        headers = {"Authorization": f"Bearer {DAILY_API_KEY}"}
        payload = {
            "properties": {
                "exp": int(timezone.now().timestamp()) + 3600,  # expires in 1 hour
                "privacy": "private",
                "enable_screenshare": True,
                "enable_chat": True
            }
        }
        response = requests.post(DAILY_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            room_data = response.json()
            appointment.video_room_url = room_data.get("url")
            appointment.save()
        else:
            return render(request, 'appointments/video_error.html', {
                'message': "Failed to create a video room. Please try again later."
            })

    # Show the call interface
    return render(request, 'appointments/video_call.html', {
        'video_link': appointment.video_room_url,
        'appointment': appointment
    })
    

from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Appointment
from .models import RescheduleForm



@login_required
def reschedule_request(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient)

    if request.method == 'POST':
        form = RescheduleForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save(commit=False)
            
            # Save original datetime only if not already set
            if not appointment.original_date or not appointment.original_time:
                appointment.original_date = appointment.date.date()
                appointment.original_time = appointment.date.time()

            # Save proposed datetime separately
            proposed_datetime = form.cleaned_data.get('date')
            if proposed_datetime:
                appointment.proposed_date = proposed_datetime.date()
                appointment.proposed_time = proposed_datetime.time()

            appointment.status = 'Reschedule Requested'
            appointment.save()
            messages.success(request, "Reschedule request sent. Waiting for doctor's approval.")
            return redirect('appointments:appointment_list')

    else:
        form = RescheduleForm(instance=appointment)

    # Combine original and proposed datetime for template
    original_dt = None
    proposed_dt = None
    if appointment.original_date and appointment.original_time:
        original_dt = datetime.combine(appointment.original_date, appointment.original_time)
    if appointment.proposed_date and appointment.proposed_time:
        proposed_dt = datetime.combine(appointment.proposed_date, appointment.proposed_time)

    return render(request, 'appointments/reschedule_form.html', {
        'form': form,
        'appointment': appointment,
        'original_dt': original_dt,
        'proposed_dt': proposed_dt,
    })


from datetime import datetime, time as dt_time

@login_required
def approve_reschedule(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)


    # Move proposed to current datetime
    if appointment.proposed_date or appointment.proposed_time:
        # Use existing date/time if proposed is None
        new_date = appointment.proposed_date or appointment.date.date()
        new_time = appointment.proposed_time or appointment.date.time()
        appointment.date = datetime.combine(new_date, new_time)

    appointment.status = "Reschedule Approved"
    # Clear proposed fields
    appointment.proposed_date = None
    appointment.proposed_time = None
    appointment.save()

    messages.success(request, "Reschedule request approved — appointment updated.")
    return redirect('dashboard_admin')



@login_required
def reject_reschedule(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Cancel the appointment on rejection
    appointment.status = "Cancelled"
    appointment.save()

    messages.warning(request, "Reschedule request rejected and appointment cancelled.")
    return redirect('dashboard_admin')

from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from users.models import User, Doctor, DoctorRegistrationRequest
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from users.models import User

# views.py

@login_required
def report_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    report = Report.objects.filter(appointment=appointment).first()  # safe fetch

    # Doctor view
    if request.user.role == 'doctor':
        today = timezone.localdate()
        app_date = appointment.date.date()

        # If report exists, show form (editable) only if it's today
        if report and appointment.status != "Completed":
            if request.method == "POST":
                form = ReportForm(request.POST, instance=report)
                if form.is_valid():
                    form.save()
                    appointment.status = "Completed"
                    appointment.save()
                    messages.success(request, "✅ Report saved! Appointment marked as completed.")
                    return redirect('appointments:dashboard_doctor')
            else:
                form = ReportForm(instance=report)
            return render(request, 'appointments/report_form.html', {
                'form': form,
                'appointment': appointment,
                'report': report,
                'doctor_view': True
            })

        # Only create report on the day of appointment
        if not report and today == app_date:
            report = Report.objects.create(
                appointment=appointment,
                doctor=request.user.doctor,
                patient=appointment.patient
            )
            form = ReportForm(instance=report)
            return render(request, 'appointments/report_form.html', {
                'form': form,
                'appointment': appointment,
                'report': report,
                'doctor_view': True
            })

        # If not today and report doesn't exist, show error
        if not report:
            messages.error(request, "⚠️ You can only create a report on the day of the appointment.")
            return redirect('appointments:dashboard_doctor')

    # Patient view or completed report (read-only)
    if report:
        return render(request, 'appointments/report_view.html', {
            'report': report,
            'appointment': appointment,
            'readonly': True
        })

    messages.info(request, "Report is not yet available. Please check back later.")
    return redirect('appointments:dashboard_patient')



    # Doctor: create/edit report
    
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Appointment

from django.utils import timezone
from appointments.models import Appointment

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from appointments.models import Appointment

@login_required
def dashboard_doctor(request):
    if request.user.role != 'doctor':
        return redirect('/')

    now = timezone.now()

    appointments = Appointment.objects.filter(doctor=request.user.doctor).order_by('-date')

    context = {
        'appointments': appointments,
        'now': timezone.localtime(now),
    }

    return render(request, 'appointments/dashboard_doctor.html', context)


from django.utils import timezone
from django.shortcuts import render
from .models import Appointment, Doctor, Patient

from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Count
from .models import Appointment, Doctor, Patient

from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Min
from .models import Appointment, Doctor, Patient

@login_required
def dashboard_patient(request):
    if request.user.role != 'patient':
        return redirect('/')

    # Ensure patient object exists
    patient, _ = Patient.objects.get_or_create(user=request.user)

    # Predefined doctor
    doctor = Doctor.objects.first()

    # Count total appointments for this patient
    total_appointments = Appointment.objects.filter(patient=patient).count()

    return render(request, 'users/dashboard_patient.html', {
        'doctors': [doctor] if doctor else [],
        'total_appointments': total_appointments,
    })
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.http import HttpResponse
# users/views.py
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import Appointment

def report_pdf_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    report = getattr(appointment, 'report', None)

    template_path = 'users/report_pdf.html'  # PDF-specific template
    context = {'appointment': appointment, 'report': report}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{appointment.patient.user.username}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF")
    return response  
