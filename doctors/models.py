"""
Models for the doctors app.
Defines DoctorProfile which stores doctor-specific details.
"""

from django.db import models
from django.conf import settings


class DoctorProfile(models.Model):
    """
    Extended profile for a user with role='doctor'.

    Attributes:
        user (User): One-to-one link to the User.
        specialization (str): e.g. 'Cardiologist'.
        experience_years (int): Years of practice.
        consultation_fee (decimal): Fee per consultation.
        bio (str): Short description about the doctor.
        is_available (bool): Whether accepting new patients.
        created_at (datetime): Auto-set when created.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        help_text="The User account this profile belongs to."
    )
    specialization = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """Return a readable label for admin display."""
        return f"Dr. {self.user.username} ({self.specialization})"

    

class AvailabilitySlot(models.Model):
    """
    A time slot during which a doctor is available.

    A patient can book one slot at a time (slot becomes booked).
    Past slots cannot be created.

    Attributes:
        doctor (DoctorProfile): Which doctor.
        date (date): Date of the slot.
        start_time (time): Start time.
        end_time (time): End time.
        is_booked (bool): True if a patient booked it.
        created_at (datetime): Auto-set when created.
    """

    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='slots',
        help_text="The doctor who owns this slot."
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')
        ordering = ['date', 'start_time']

    def __str__(self):
        """Return a readable label for admin display."""
        return f"Dr. {self.doctor.user.username} - {self.date} {self.start_time}"