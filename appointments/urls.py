"""
URL routes for the appointments app.

Patient endpoints:
    POST   /api/appointments/book/                - Request an appointment
    GET    /api/my-appointments/                  - List own appointments
    PUT    /api/appointments/<id>/cancel/         - Cancel own appointment

Doctor endpoints:
    GET    /api/doctor/appointments/              - List doctor's appointments
    PUT    /api/appointments/<id>/approve/        - Accept a request
    PUT    /api/appointments/<id>/reject/         - Reject a request
    PUT    /api/appointments/<id>/status/         - Mark completed/no_show
    PUT    /api/appointments/<id>/notes/          - Add prescription notes
"""

from django.urls import path
from .views import (
    book_appointment,
    my_appointments,
    cancel_appointment,
    doctor_appointments,
    approve_appointment,
    reject_appointment,
    update_appointment_status,
    add_appointment_notes,
)

urlpatterns = [
    # -------- Patient endpoints --------
    path('appointments/book/',book_appointment,name='book_appointment'),
    path('my-appointments/',my_appointments,name='my_appointments'),
    path('appointments/<int:appointment_id>/cancel/',cancel_appointment,name='cancel_appointment'),

    # -------- Doctor endpoints --------
    path('doctor/appointments/',doctor_appointments,name='doctor_appointments'),
    path('appointments/<int:appointment_id>/approve/',approve_appointment,name='approve_appointment'),
    path('appointments/<int:appointment_id>/reject/',reject_appointment,name='reject_appointment'),
    path( 'appointments/<int:appointment_id>/status/', update_appointment_status, name='update_status'),
    path( 'appointments/<int:appointment_id>/notes/', add_appointment_notes, name='add_notes'),
]