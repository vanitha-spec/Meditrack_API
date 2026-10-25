"""
URL routes for the doctors app.
"""

from django.urls import path
from .views import (
    create_or_update_profile, list_doctors, doctor_detail,
    create_slot, list_slots, delete_slot,
)

urlpatterns = [
    # Doctor profile endpoints
    path('doctors/', list_doctors, name='list_doctors'),
    path('doctors/profile/', create_or_update_profile, name='doctor_profile'),
    path('doctors/<int:doctor_id>/', doctor_detail, name='doctor_detail'),

    # Availability slot endpoints
    path('slots/', list_slots, name='list_slots'),
    path('slots/create/', create_slot, name='create_slot'),
    path('slots/<int:slot_id>/delete/', delete_slot, name='delete_slot'),
]