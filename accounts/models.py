"""
Models for the accounts app.
Defines a custom User model with a 'role' field so we can
distinguish between doctors and patients.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model that extends Django's default AbstractUser.

    Adds a 'role' field to identify whether the user is a
    doctor (who provides consultations) or a patient (who books them).

    Attributes:
        role (str): Either 'doctor' or 'patient'.
    """

    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='patient',
        help_text="Role of the user: doctor or patient."
    )

    def is_doctor(self):
        """
        Check if the user is a doctor.

        Returns:
            bool: True if role is 'doctor', else False.
        """
        return self.role == 'doctor'

    def is_patient(self):
        """
        Check if the user is a patient.

        Returns:
            bool: True if role is 'patient', else False.
        """
        return self.role == 'patient'

    def __str__(self):
        """Return username with role for admin display."""
        return f"{self.username} ({self.role})"