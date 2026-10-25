"""
Models for the appointments app.
Defines the Appointment model linking patients to slots.
"""

from django.db import models
from django.conf import settings
from doctors.models import AvailabilitySlot


class Appointment(models.Model):
    """
    A booked appointment between a patient and a doctor's slot.

    Lifecycle:
        1. Patient requests a slot → status = 'requested'
        2. Doctor accepts → status = 'accepted' (slot marked booked)
        3. Doctor rejects → status = 'rejected' (slot stays free)
        4. After consultation → 'completed' or 'no_show'
        5. Patient can 'cancel' before acceptance

    Attributes:
        slot (AvailabilitySlot): The requested slot.
        patient (User): The patient who requested it.
        status (str): requested / accepted / rejected / completed /
                      cancelled / no_show.
        notes (str): Doctor's notes after the visit.
        created_at (datetime): Auto-set when created.
    """

    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )

    slot = models.OneToOneField(
        AvailabilitySlot,
        on_delete=models.CASCADE,
        related_name='appointment',
        help_text="The slot this appointment is booked for."
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        help_text="The patient who requested this appointment."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='requested',
        help_text="Current state of the appointment."
    )
    notes = models.TextField(
        blank=True,
        help_text="Doctor's notes / prescription after the visit."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """Return a readable label for admin display."""
        return (
            f"{self.patient.username} → "
            f"Dr. {self.slot.doctor.user.username} ({self.status})"
        )