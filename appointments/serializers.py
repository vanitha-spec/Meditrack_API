"""
Serializers for the appointments app.
"""

from rest_framework import serializers
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Appointment.

    Includes read-only nested info:
        - patient username
        - doctor username and specialization
        - slot date and times
    """

    patient_username = serializers.CharField(
        source='patient.username', read_only=True
    )
    doctor_username = serializers.CharField(
        source='slot.doctor.user.username', read_only=True
    )
    doctor_specialization = serializers.CharField(
        source='slot.doctor.specialization', read_only=True
    )
    slot_date = serializers.DateField(source='slot.date', read_only=True)
    slot_start = serializers.TimeField(source='slot.start_time', read_only=True)
    slot_end = serializers.TimeField(source='slot.end_time', read_only=True)

    class Meta:
        model = Appointment
        fields = (
            'id',
            'slot',
            'patient',
            'patient_username',
            'doctor_username',
            'doctor_specialization',
            'slot_date',
            'slot_start',
            'slot_end',
            'status',
            'notes',
            'created_at',
        )
        read_only_fields = (
            'id', 'patient', 'status', 'notes', 'created_at'
        )
        extra_kwargs = {
            'slot': {'required': False, 'write_only': True}
        }