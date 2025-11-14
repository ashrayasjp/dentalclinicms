from django.urls import path
from .views import  predict_disease

urlpatterns = [
    path('predict_disease/', predict_disease, name='predict_disease'),
]