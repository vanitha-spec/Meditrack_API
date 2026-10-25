"""
Main URL configuration for MediTrack.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from appointments.views import (
    page_login, page_register, page_doctors,
    page_my_appointments, page_doctor_dashboard,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API routes
    path('api/', include('accounts.urls')),
    path('api/', include('doctors.urls')),
    path('api/', include('appointments.urls')),

    # Frontend pages
    path('', page_login, name='home'),
    path('login/', page_login, name='page_login'),
    path('register/', page_register, name='page_register'),
    path('doctors/', page_doctors, name='page_doctors'),
    path('my-appointments/', page_my_appointments, name='page_my_appointments'),
    path('doctor/', page_doctor_dashboard, name='page_doctor_dashboard'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)