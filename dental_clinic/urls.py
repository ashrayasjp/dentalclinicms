from django.contrib import admin
from django.urls import path, include
from users.views import home_view
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
     path('', include('users.urls')),                 # Home page
    path('accounts/', include('users.urls')),             # Users app (login, register, dashboards)
    path('appointments/', include('appointments.urls')), 
    path('ai/', include('ai.urls')),


]# Appointments app

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)