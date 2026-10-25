"""
Admin configuration for the appointments app.
"""

from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin view for Appointment."""

    list_display = ('patient', 'slot', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__username', 'slot__doctor__user__username')