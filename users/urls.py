from django.urls import path, include
from .views import *
from django.contrib.auth.views import LogoutView
urlpatterns = [
    # Authentication
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
   path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('check-username/', check_username, name='check_username'),
    path('check-email/', check_email, name='check_email'),
       path('send_reply_ajax/', send_reply_ajax, name='send_reply_ajax'),
       path('send_patient_reply_ajax/', send_patient_reply_ajax, name='send_patient_reply_ajax'),
 path('get_patient_messages/', get_patient_messages, name='get_patient_messages'),

    path('send-reply/<int:message_id>/', send_reply, name='send_reply'),
path('patient_messages/', patient_messages, name='patient_messages'),

    path('', home, name='home'),  # Home page
    # Dashboards
    path('dashboard/admin/', dashboard_admin, name='dashboard_admin'),
     path('admin/notifications/', notifications_page, name='notifications_page'),

    # Users page (Registered doctors and patients)
    path('admin/users/', users_page, name='users_page'),

    path('dashboard/doctor/', dashboard_doctor, name='dashboard_doctor'),
    path('dashboard/patient/', dashboard_patient, name='dashboard_patient'),
    
path('dashboard/admin/approve-doctor/<int:request_id>/', approve_doctor_request, name='approve_doctor_request'),
path('admin/reject-doctor/<int:request_id>/', reject_doctor_request, name='reject_doctor_request'),
    # Admin Doctor Management
    path('doctor-requests/', doctor_requests, name='doctor_requests'),
    path('admin/doctors/', manage_doctors, name='manage_doctors'),
    path('admin/doctors/add/', add_doctor, name='add_doctor'),
    path('admin/doctors/edit/<int:doctor_id>/', edit_doctor, name='edit_doctor'),
    path('admin/doctors/delete/<int:doctor_id>/', delete_doctor, name='delete_doctor'),
    path('dashboard/patient/pay-esewa/<int:appointment_id>/', pay_esewa_redirect, name='pay_esewa_redirect'),
   

]
