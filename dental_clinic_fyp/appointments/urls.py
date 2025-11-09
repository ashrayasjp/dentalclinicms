from django.urls import path
from . import views

app_name = 'appointments'

# urls.py
urlpatterns = [
    path('dashboard/patient/', views.dashboard_patient, name='dashboard_patient'),
    path('create/', views.create_appointment, name='create_appointment'),
    path('list/', views.appointment_list, name='appointment_list'),
    path('doctor/', views.doctor_appointments, name='doctor_appointments'),
    path('detail/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('doctor/<int:doctor_id>/details/', views.doctor_details, name='doctor_details'),
    path('all-doctors/', views.all_doctors, name='all_doctors'),


     path('pay/esewa/success/<int:appointment_id>/', views.esewa_success, name='esewa_success'),
    path('pay/esewa/failure/<int:appointment_id>/', views.esewa_failure, name='esewa_failure'),
    path('dashboard/patient/pay-esewa/<int:appointment_id>/', views.pay_esewa_redirect, name='pay_esewa_redirect'),
    path('pay/mock/<int:appointment_id>/', views.mock_payment, name='mock_payment'),
    path('pay/esewa/<int:appointment_id>/', views.esewa_payment_page, name='esewa_payment_page'),
    path('video/<int:appointment_id>/', views.start_video_call, name='start_video_call'),
    path('reschedule/<int:appointment_id>/', views.reschedule_request, name='reschedule_request'),
    path('reschedule/approve/<int:appointment_id>/', views.approve_reschedule, name='approve_reschedule'),
    path('reschedule/reject/<int:appointment_id>/', views.reject_reschedule, name='reject_reschedule'),
    path('report/<int:appointment_id>/', views.report_detail, name='report_detail'),
      path('doctor/dashboard/', views.dashboard_doctor, name='dashboard_doctor'),
       path('report/<int:appointment_id>/pdf/', views.report_pdf_view, name='report_pdf'),
    
]



