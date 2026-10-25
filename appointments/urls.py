"""
URL routes for the appointments app.
"""

from django.urls import path
from .views import (
    book_appointment,
    my_appointments,
    cancel_appointment,
    doctor_appointments,
    update_appointment_status,
    add_appointment_notes,
)

urlpatterns = [
    # Patient endpoints
    path('appointments/book/', book_appointment, name='book_appointment'),
    path('my-appointments/', my_appointments, name='my_appointments'),
    path('appointments/<int:appointment_id>/cancel/', cancel_appointment, name='cancel_appointment'),

    # Doctor endpoints
    path('doctor/appointments/', doctor_appointments, name='doctor_appointments'),
    path('appointments/<int:appointment_id>/status/', update_appointment_status, name='update_status'),
    path('appointments/<int:appointment_id>/notes/', add_appointment_notes, name='add_notes'),
]