"""
Serializers for the doctors app.
Converts DoctorProfile model instances to/from JSON.
"""

from rest_framework import serializers
from .models import DoctorProfile


class DoctorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for DoctorProfile.

    Exposes username and email (read-only) so clients know
    which doctor each profile belongs to.
    """

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = DoctorProfile
        fields = (
            'id',
            'user',
            'username',
            'email',
            'specialization',
            'experience_years',
            'consultation_fee',
            'bio',
            'is_available',
            'created_at',
        )
        read_only_fields = ('id', 'user', 'created_at')

    def validate_experience_years(self, value):
        """
        Ensure experience is between 0 and 60 years.

        Args:
            value (int): Years of experience.

        Returns:
            int: Validated value.

        Raises:
            ValidationError: If out of range.
        """
        if value < 0 or value > 60:
            raise serializers.ValidationError(
                "Experience must be between 0 and 60 years."
            )
        return value

    def validate_consultation_fee(self, value):
        """
        Ensure consultation fee is not negative.

        Args:
            value (Decimal): Consultation fee.

        Returns:
            Decimal: Validated value.

        Raises:
            ValidationError: If negative.
        """
        if value < 0:
            raise serializers.ValidationError(
                "Consultation fee cannot be negative."
            )
        return value


from .models import DoctorProfile, AvailabilitySlot


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    """
    Serializer for AvailabilitySlot.

    Includes read-only fields for doctor's username and specialization
    so clients know who the slot belongs to.
    """

    doctor_username = serializers.CharField(
        source='doctor.user.username', read_only=True
    )
    doctor_specialization = serializers.CharField(
        source='doctor.specialization', read_only=True
    )

    class Meta:
        model = AvailabilitySlot
        fields = (
            'id',
            'doctor',
            'doctor_username',
            'doctor_specialization',
            'date',
            'start_time',
            'end_time',
            'is_booked',
            'created_at',
        )
        read_only_fields = ('id', 'doctor', 'is_booked', 'created_at')

    def validate(self, data):
        """
        Validate that:
          - end_time is after start_time
          - slot date is not in the past

        Args:
            data (dict): Slot input data.

        Returns:
            dict: Validated data.

        Raises:
            ValidationError: If any rule is violated.
        """
        from datetime import date as today_date

        start = data.get('start_time')
        end = data.get('end_time')
        slot_date = data.get('date')

        if start and end and end <= start:
            raise serializers.ValidationError(
                "End time must be after start time."
            )

        if slot_date and slot_date < today_date.today():
            raise serializers.ValidationError(
                "Slot date cannot be in the past."
            )

        return data