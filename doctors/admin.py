"""
Admin configuration for the doctors app.
"""

from django.contrib import admin
from .models import DoctorProfile, AvailabilitySlot


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    """Admin view for DoctorProfile."""

    list_display = ('user', 'specialization', 'experience_years',
                    'consultation_fee', 'is_available')
    list_filter = ('specialization', 'is_available')
    search_fields = ('user__username', 'specialization')


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    """Admin view for AvailabilitySlot."""

    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('date', 'is_booked')
    search_fields = ('doctor__user__username',)