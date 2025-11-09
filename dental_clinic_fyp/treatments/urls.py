from django.urls import path
from .views import treatment_form,treatment_history

urlpatterns=[
    path('add/',treatment_form,name='treatment_form'),
    path('history/',treatment_history,name='treatment_history'),
]
