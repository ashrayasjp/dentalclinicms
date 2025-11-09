from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User, Doctor, Patient
from django.shortcuts import render


from django.contrib.auth.hashers import make_password
from .models import User, Patient, Doctor, DoctorRegistrationRequest  # make sure to import request model



import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import DoctorRegistrationRequest, Patient

User = get_user_model()

import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Patient, DoctorRegistrationRequest

def register_view(request):
    if request.method == 'POST':
        # --- Get POST data ---
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        contact = request.POST.get('contact', '').strip()
        blood_group = request.POST.get('blood_group', '').strip()
        role = request.POST.get('role', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        identity_document = request.FILES.get('identity_document')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('address', '')
        profile_picture = request.FILES.get('profile_picture')  # doctor
        degree = request.POST.get('degree', '').strip()
        specialization = request.POST.get('specialization', '').strip()  # new
        experience_years = request.POST.get('experience_years', '').strip()  # new
        bio = request.POST.get('bio', '').strip()  # new

        form_data = request.POST.copy()  # To persist form on error

        # --- Server-side validations ---
        required_fields = [username, first_name, last_name, email, contact, blood_group, role, password1, password2, gender, age]
        if not all(required_fields):
            messages.error(request, "Please fill all required fields.")
            return render(request, "users/register.html", {'form_data': form_data})

        if len(username) < 4:
            messages.error(request, "Username must be at least 4 characters.")
            return render(request, "users/register.html", {'form_data': form_data})

        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            messages.error(request, "Enter a valid email address.")
            return render(request, "users/register.html", {'form_data': form_data})

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "users/register.html", {'form_data': form_data})

        pw_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{6,}$'
        if not re.match(pw_regex, password1):
            messages.error(request, "Weak password: min 6 chars, uppercase, lowercase, number, special char.")
            return render(request, "users/register.html", {'form_data': form_data})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "users/register.html", {'form_data': form_data})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "users/register.html", {'form_data': form_data})

        # --- Registration ---
        if role == "doctor":
            # Doctor-specific required fields
            if not identity_document:
                messages.error(request, "Please upload your identity document.")
                return render(request, "users/register.html", {'form_data': form_data})

            if not degree:
                messages.error(request, "Please enter your degree.")
                return render(request, "users/register.html", {'form_data': form_data})

            if not profile_picture:
                messages.error(request, "Please upload your profile picture.")
                return render(request, "users/register.html", {'form_data': form_data})

            # Create doctor registration request
            DoctorRegistrationRequest.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                contact=contact,
                blood_group=blood_group,
                identity_document=identity_document,
                profile_picture=profile_picture,
                degree=degree,
                specialization=specialization,
                experience_years=int(experience_years) if experience_years else 0,
                bio=bio,
                password=password1,  # store plain password for admin approval
            )

            messages.success(request, "Your registration request has been submitted for admin approval.")
            return redirect("login")

        else:  # Patient registration
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password1,  # automatically hashed
                role="patient",
                blood_group=blood_group,
                phone_number=contact,
                is_approved=True,
                is_active=True,
                gender=gender,
                age=age if age else None
            )

            # Create corresponding Patient object
            Patient.objects.create(
                user=user,
                contact=contact,
                address=address,
                age=age if age else None,
                gender=gender
            )

            messages.success(request, "Account created successfully! You can now log in.")
            return redirect("login")

    return render(request, "users/register.html")


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        # Redirect logged-in users to their respective dashboards
        if request.user.role == 'admin':
            return redirect('dashboard_admin')
        elif request.user.role == 'doctor':
            return redirect('dashboard_doctor')
        else:
            return redirect('dashboard_patient')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if username exists
        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Username not found.")
            return render(request, 'users/login.html', {'username': username})

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is inactive. Please contact admin.")
                return render(request, 'users/login.html', {'username': username})

            login(request, user)

            # Redirect based on role
            if user.role == 'admin':
                return redirect('dashboard_admin')
            elif user.role == 'doctor':
                return redirect('dashboard_doctor')
            else:
                return redirect('appointments:create_appointment')
        else:
            messages.error(request, "Incorrect password.")

    return render(request, 'users/login.html')



# Dashboards
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from appointments.models import Appointment

from users.models import Doctor, Patient


@login_required
@user_passes_test(lambda u: u.is_authenticated and u.role == 'admin')
def dashboard_admin(request):
    # Pending doctor registration requests
    requests = DoctorRegistrationRequest.objects.filter(is_approved=False)
    
    # All doctors and patients
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    
    # Latest messages
    messages_list = ContactMessage.objects.order_by('-created_at')[:5]
    
    # Latest patient reasons (formerly notes)
    patient_reasons = Appointment.objects.exclude(notes__isnull=True)\
                                         .exclude(notes__exact='')\
                                         .order_by('-date')[:10]
    
    return render(request, "users/dashboard_admin.html", {
        "requests": requests,
        "doctors": doctors,
        "patients": patients,
        "messages_list": messages_list,
        "patient_reasons": patient_reasons,  # pass reasons to template
    })


# Notifications page
@login_required
@user_passes_test(lambda u: u.is_authenticated and u.role == 'admin')
def notifications_page(request):
    messages_list = ContactMessage.objects.order_by('-created_at')
    return render(request, "users/notifications.html", {"messages_list": messages_list})

# Users page
@login_required
@user_passes_test(lambda u: u.is_authenticated and u.role == 'admin')
def users_page(request):
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    return render(request, "users/users_page.html", {
        "doctors": doctors,
        "patients": patients
    })

from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from django.contrib.auth.hashers import make_password

from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from users.models import User, Doctor, DoctorRegistrationRequest
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from users.models import User
def approve_doctor_view(request, request_id):
    # Get the pending doctor request
    doctor_request = get_object_or_404(DoctorRegistrationRequest, id=request_id)

    # Check if username or email already exists in Users
    if User.objects.filter(username=doctor_request.username).exists():
        messages.error(request, f"Username '{doctor_request.username}' is already taken.")
        return redirect('dashboard_admin')  # or wherever your list is

    if User.objects.filter(email=doctor_request.email).exists():
        messages.error(request, f"Email '{doctor_request.email}' is already registered.")
        return redirect('doctor_requests_list')

    # Create the user
    user = User.objects.create_user(
        username=doctor_request.username,
        first_name=doctor_request.first_name,
        last_name=doctor_request.last_name,
        email=doctor_request.email,
        password=doctor_request.password,  # already hashed in registration request
        role='doctor',
        blood_group=doctor_request.blood_group,
        phone_number=doctor_request.contact
    )

    # Create Doctor profile
    Doctor.objects.create(user=user)

    # Delete the registration request
    doctor_request.delete()

    messages.success(request, f"Doctor '{user.get_full_name()}' approved successfully!")
    return redirect('doctor_requests_list')



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from  appointments.models import Appointment, Doctor

@login_required
def dashboard_doctor(request):
    # Ensure user is a doctor
    if request.user.role != 'doctor':
        messages.error(request, "Access denied.")
        return redirect('login')

    # Get the doctor profile linked to the logged-in user
    doctor = Doctor.objects.get(user=request.user)

    # Fetch appointments for this doctor
    appointments = Appointment.objects.filter(doctor=doctor).order_by('date')

    return render(request, 'appointments/dashboard_doctor.html', {
        'appointments': appointments
    })



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

# Admin decorator
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'admin')(view_func)

# Doctor management
@admin_required
def manage_doctors(request):
    doctors = Doctor.objects.all()
    return render(request, 'users/manage_doctors.html', {'doctors': doctors})

@admin_required
def add_doctor(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        available = 'available' in request.POST
        user = User.objects.create_user(username=username, password=password, role='doctor',
                                        first_name=first_name, last_name=last_name)
        Doctor.objects.create(user=user, available=available)
        return redirect('manage_doctors')
    return render(request, 'users/add_doctor.html')

@admin_required
def edit_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        doctor.user.username = request.POST['username']
        doctor.user.first_name = request.POST['first_name']
        doctor.user.last_name = request.POST['last_name']
        doctor.user.save()
        doctor.department = request.POST['department']
        doctor.available = 'available' in request.POST
        doctor.save()
        return redirect('manage_doctors')
    return render(request, 'users/edit_doctor.html', {'doctor': doctor})

@admin_required
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.user.delete()
    return redirect('manage_doctors')



def home_view(request):
    """Landing page for the dental clinic."""
    return render(request, 'users/home.html')
@login_required
def pay_esewa_redirect(request,  appointment_id):
    if request.method == 'POST':
        amount = request.POST.get('amount', '1000')
        appointment_id = request.POST.get('appointment_id')

        esewa_data = {
            'amt': amount,
            'tAmt': amount,
            'txAmt': '0',
            'psc': '0',
            'pdc': '0',
            'pid': appointment_id,
            'scd': 'EPAYTEST',
            'su': 'http://127.0.0.1:8000/payment/success/',
            'fu': 'http://127.0.0.1:8000/payment/failure/',
            'receiver': '9823588827'
        }

        return render(request, 'users/esewa_redirect.html', {'esewa_data': esewa_data})

    return redirect('appointments:appointment_list')

from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'exists': exists})

def check_email(request):
    email = request.GET.get('email', '')
    exists = User.objects.filter(email__iexact=email).exists()
    return JsonResponse({'exists': exists})

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DoctorRegistrationRequest

def doctor_requests(request):
    requests = DoctorRegistrationRequest.objects.all()
    return render(request, 'users/doctor_requests.html', {'requests': requests})


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from users.models import DoctorRegistrationRequest, User, Doctor

# Only superuser can approve doctors
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from users.models import User, Doctor



from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from users.models import User, Doctor, DoctorRegistrationRequest

def superuser_required(user):
    return user.is_superuser

@user_passes_test(lambda u: u.is_superuser)


@login_required
def dashboard_admin(request):
    # ===================== Reschedule Requested Appointments =====================
    appointments = Appointment.objects.filter(status="Reschedule Requested").select_related(
        'patient__user', 'doctor__user'
    )

    now = timezone.now()

    # Prepare list with combined original and proposed datetimes
    appointment_list = []
    for appt in appointments:
        # Original datetime
        original_dt = None
        if appt.original_date and appt.original_time:
            original_dt = datetime.combine(appt.original_date, appt.original_time)

        # Proposed datetime
        proposed_dt = None
        if appt.proposed_date and appt.proposed_time:
            proposed_dt = datetime.combine(appt.proposed_date, appt.proposed_time)

        appointment_list.append({
            'appointment': appt,
            'original_dt': original_dt,
            'proposed_dt': proposed_dt,
        })

    # ===================== Doctor Requests =====================
    doctor_requests = DoctorRegistrationRequest.objects.all()  # show all, not just pending
    has_pending_requests = doctor_requests.filter(status='Pending').exists()
    # ===================== Other Info =====================
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    messages_list = ContactMessage.objects.order_by('-created_at')[:5]  # latest 5 messages

    context = {
        'appointments': appointment_list,
        'now': now,
        'requests': doctor_requests,
        'doctors': doctors,
        'patients': patients,
        'messages_list': messages_list,
    }

    return render(request, 'users/dashboard_admin.html', context)



@user_passes_test(lambda u: u.is_superuser)
def approve_doctor_request(request, request_id):
    # Get pending request
    doctor_request = get_object_or_404(DoctorRegistrationRequest, id=request_id, status='Pending')

    # Check if a user with same username or email exists
    existing_user = (
        User.objects.filter(username=doctor_request.username).first() or
        User.objects.filter(email=doctor_request.email).first()
    )

    # If user exists and has a doctor profile, reject
    if existing_user and hasattr(existing_user, "doctor"):
        messages.error(request, f"Doctor '{existing_user.username}' already exists.")
        doctor_request.status = 'Rejected'
        doctor_request.save()
        return redirect("dashboard_admin")

    # Create new user if necessary
    if not existing_user:
        user = User.objects.create(
            username=doctor_request.username,
            first_name=doctor_request.first_name,
            last_name=doctor_request.last_name,
            email=doctor_request.email,
            role='doctor',
            blood_group=doctor_request.blood_group,
            phone_number=doctor_request.contact,
            is_active=True,
            is_approved=True,
        )
        user.set_password(doctor_request.password)
        user.save()
    else:
        user = existing_user

    # Create full Doctor profile
    doctor, created = Doctor.objects.update_or_create(
    user=user,
    defaults={
        "degree": doctor_request.degree,
        "specialization": doctor_request.specialization,
        "experience_years": doctor_request.experience_years,
        "bio": doctor_request.bio,
        "profile_picture": doctor_request.profile_picture,
        "identity_document": doctor_request.identity_document,
    }
)


    # Mark request as approved
    doctor_request.is_approved = True
    doctor_request.status = 'Approved'
    doctor_request.save()

    messages.success(request, f"Doctor '{user.get_full_name() or user.username}' approved successfully.")
    return redirect("dashboard_admin")

@user_passes_test(lambda u: u.is_superuser)
def reject_doctor_request(request, request_id):
    doctor_request = get_object_or_404(DoctorRegistrationRequest, id=request_id)
    doctor_request.status = 'Rejected'
    doctor_request.is_approved = False
    doctor_request.save()
    messages.warning(request, f"Doctor request for '{doctor_request.username}' rejected.")
    return redirect("dashboard_admin")


# views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import ContactMessage, Reply, MessageReply




@login_required
def send_admin_reply_ajax(request):
    if request.method == "POST" and request.user.is_staff:
        data = json.loads(request.body)
        msg_id = data.get("msg_id")
        reply_text = data.get("reply_message")

        if not reply_text:
            return JsonResponse({"success": False, "error": "Empty message"})

        msg = get_object_or_404(ContactMessage, id=msg_id)

        reply = MessageReply.objects.create(
            parent=msg,
            sender=request.user,  # admin
            reply_message=reply_text,
            created_at=timezone.now()
        )

        msg.replied = True
        msg.save()

        return JsonResponse({
            "success": True,
            "reply_message": reply.reply_message,
            "timestamp": reply.created_at.strftime("%b %d, %Y %H:%M"),
            "sender": reply.sender.username
        })

    return JsonResponse({"success": False, "error": "Invalid request"})

@login_required
def get_admin_messages_ajax(request):
    if not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Not authorized"})

    messages = ContactMessage.objects.all().order_by('-created_at')
    data = []

    for msg in messages:
        all_msgs = list(msg.all_replies.all())
        all_msgs.sort(key=lambda x: x.created_at)

        msg_data = {
            "id": msg.id,
            "name": msg.name,
            "all_msgs": []
        }

        # Include original message first
        msg_data["all_msgs"].append({
            "sender": msg.name,
            "message_text": msg.message,
            "created_at": msg.created_at.strftime("%b %d, %Y %H:%M")
        })

        for r in all_msgs:
            sender_name = r.sender.username if r.sender else "Admin"
            msg_data["all_msgs"].append({
                "sender": sender_name,
                "message_text": r.reply_message,
                "created_at": r.created_at.strftime("%b %d, %Y %H:%M")
            })

        data.append(msg_data)

    return JsonResponse({"success": True, "messages": data})



@login_required
def send_patient_reply_ajax(request):
    if request.method == "POST" and request.user.role == "patient":
        data = json.loads(request.body)
        msg_id = data.get("msg_id")
        reply_text = data.get("reply_message")

        if not reply_text:
            return JsonResponse({"success": False, "error": "Empty message"})

        msg = get_object_or_404(ContactMessage, id=msg_id)

        reply = MessageReply.objects.create(
            parent=msg,
            sender=request.user,  # patient
            reply_message=reply_text,
            created_at=timezone.now()
        )

        return JsonResponse({
            "success": True,
            "reply_message": reply.reply_message,
            "timestamp": reply.created_at.strftime("%b %d, %Y %H:%M"),
            "sender": reply.sender.username
        })

    return JsonResponse({"success": False, "error": "Invalid request"})




@login_required
def patient_messages_widget(request):
    if request.user.role != 'patient':
        return JsonResponse({"error": "Not authorized"}, status=403)

    # Fetch messages sent to this patient
    messages_list = ContactMessage.objects.filter(email=request.user.email).order_by('-created_at')

    # Combine original message + replies for each message
    for msg in messages_list:
        all_msgs = list(msg.replies.all()) + [msg]  # original message at end
        all_msgs.sort(key=lambda x: x.created_at)  # sort by time ascending
        msg.all_msgs = all_msgs

    return render(request, "users/patient_messages_widget.html", {"messages_list": messages_list})

# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
from .models import ContactMessage, Reply

@login_required

def send_reply_ajax(request):
    if request.method == "POST":
        import json
        from django.utils import timezone
        from django.http import JsonResponse
        data = json.loads(request.body)
        msg_id = data.get('msg_id')
        reply_text = data.get('reply_message')

        if not reply_text:
            return JsonResponse({"success": False, "error": "Empty message"})

        try:
            msg = ContactMessage.objects.get(id=msg_id)
        except ContactMessage.DoesNotExist:
            return JsonResponse({"success": False, "error": "Message not found"})

        reply = MessageReply.objects.create(
            parent=msg,
            sender=request.user,
            reply_message=reply_text,
            created_at=timezone.now()
        )

        return JsonResponse({
            "success": True,
            "reply_message": reply.reply_message,
            "timestamp": reply.created_at.strftime("%b %d, %Y %H:%M"),
            "sender": request.user.username
        })

    return JsonResponse({"success": False, "error": "Invalid request"})


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import ContactMessage, Reply, MessageReply
import json

# Get all patient messages + replies
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import ContactMessage, Reply
import json

# views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import ContactMessage, Reply
def get_patient_messages(request):
    try:
        messages_list = ContactMessage.objects.filter(email=request.user.email).order_by('-created_at')

        if not messages_list.exists():
            return JsonResponse({"success": True, "messages": []})

        msg = messages_list.first()
        all_msgs = []

        # Original patient message
        all_msgs.append({
            "id": msg.id,
            "message_text": msg.message,
            "sender": request.user.username,  # patient as sender
            "created_at": msg.created_at.strftime("%b %d, %Y %H:%M")
        })

        # Replies from admin or patient
        for reply in msg.replies.all().order_by("created_at"):
            sender_name = reply.sender.username if reply.sender else "Admin"
            all_msgs.append({
                "id": reply.id,
                "message_text": reply.reply_message,
                "sender": sender_name,
                "created_at": reply.created_at.strftime("%b %d, %Y %H:%M")
            })

        return JsonResponse({"success": True, "messages": [{"id": msg.id, "all_msgs": all_msgs}]})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

# views.py
from django.contrib.auth import get_user_model
User = get_user_model()
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from .models import ContactMessage, Reply

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ContactMessage, Reply
import json

@login_required
def send_patient_reply_ajax(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            msg_id = data.get("msg_id")
            reply_text = data.get("reply_message").strip()
            if not reply_text:
                return JsonResponse({"success": False, "error": "Message cannot be empty."})

            user_email = request.user.email
            user_name = request.user.get_full_name() or request.user.username

            # If no msg_id provided (first message), create ContactMessage
            if not msg_id:
                contact_msg = ContactMessage.objects.create(
                    name=user_name,
                    email=user_email,
                    message=reply_text
                )
            else:
                try:
                    contact_msg = ContactMessage.objects.get(id=msg_id)
                except ContactMessage.DoesNotExist:
                    return JsonResponse({"success": False, "error": "Message not found."})

                # Create a reply linked to the ContactMessage
                Reply.objects.create(
                     message=contact_msg,
                    reply_message=reply_text,
                    sender=request.user
                )

            return JsonResponse({"success": True, "msg_id": contact_msg.id})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request."})


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import ContactMessage, Reply
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import ContactMessage, Reply

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import ContactMessage, Reply



def send_reply(request, message_id):
    msg = get_object_or_404(ContactMessage, id=message_id)

    if request.method == 'POST':
        reply_message = request.POST.get('reply_message')

        # Create Reply with sender
        Reply.objects.create(
            message=msg,
            reply_message=reply_message,
            sender=request.user  # IMPORTANT: set sender
        )

        msg.seen = True   # mark as seen by admin
        msg.save()

        messages.success(request, f"Reply sent to {msg.name} successfully!")
        return redirect('notifications_page')  # or wherever you want

@login_required
@csrf_exempt
def send_reply_ajax(request):
    if request.method == "POST":
        data = json.loads(request.body)
        msg_id = data.get("msg_id")
        reply_text = data.get("reply_message")

        msg = get_object_or_404(ContactMessage, id=msg_id)

        # Create reply with admin as sender
        reply = Reply.objects.create(
            message=msg,
            reply_message=reply_text,
            sender=request.user
        )

        msg.replied = True
        msg.save()

        return JsonResponse({
            "success": True,
            "reply_message": reply.reply_message,
            "timestamp": reply.created_at.strftime("%b %d, %Y %H:%M")
        })

    return JsonResponse({"success": False})

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db.models import Max
from .models import ContactMessage

@login_required
def patient_messages(request):
    if request.user.role != 'patient':
        return redirect('home')

    # Get the latest message per user (unique users only)
    latest_per_user = (
        ContactMessage.objects
        .filter(email=request.user.email)
        .values('name')
        .annotate(latest_id=Max('id'))
    )

    # Fetch latest messages to show in card headers
    latest_ids = [item['latest_id'] for item in latest_per_user]
    messages_list = ContactMessage.objects.filter(id__in=latest_ids).order_by('-created_at')

    
    user_messages = {}
    all_msgs = ContactMessage.objects.filter(email=request.user.email).order_by('created_at')
    for msg in all_msgs:
        
        user_messages.setdefault(msg.name, []).append(msg)

    return render(request, 'users/notifications.html', {
        'messages_list': messages_list,   
        'user_messages': user_messages,    
    })
from django.db.models import Q
from django.shortcuts import render
from .models import ContactMessage, MessageReply

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ContactMessage
from django.db.models import Max

from django.db.models import Max

@login_required
def admin_notifications(request):
    if request.user.role != 'admin':
        return redirect('home')

    # Get all patients who have sent messages
    all_messages = ContactMessage.objects.all().order_by('created_at')

    # Group messages by patient
    patient_chats = []
    patient_dict = {}

    for msg in all_messages:
        if msg.email not in patient_dict:
            patient_dict[msg.email] = {
                "name": msg.name,
                "messages": []
            }
        patient_dict[msg.email]["messages"].append(msg)

    # Convert to list for easier iteration in template
    for patient in patient_dict.values():
        patient_chats.append(patient)

    return render(request, 'users/notifications.html', {
        "patient_chats": patient_chats
    })
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from .models import ContactMessage, Reply

# views.py
from django.contrib.auth.decorators import login_required
from .models import Doctor



from users.models import DoctorRegistrationRequest

from users.models import Doctor

def home(request):
    doctors_qs = Doctor.objects.all()
    doctors = []

    for doc in doctors_qs:
        doctors.append({
            "id": doc.id,
            "full_name": f"Dr. {doc.user.first_name} {doc.user.last_name}",
            "degree": doc.degree if doc.degree else "N/A",
            "specialization": doc.specialization if doc.specialization else "N/A",
            "experience_years": doc.experience_years if doc.experience_years else 0,
            "bio": doc.bio if doc.bio else "N/A",
            "profile_picture": doc.profile_picture.url if doc.profile_picture else "/static/images/default_profile.png"
        })

    return render(request, "users/home.html", {"doctors": doctors})
# views.py


from datetime import datetime
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from appointments.models import Appointment
from django.contrib.auth.decorators import login_required

