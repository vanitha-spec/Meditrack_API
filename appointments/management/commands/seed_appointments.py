"""
Management command to seed dummy appointments.

Usage:
    python manage.py seed_appointments
"""

from django.core.management.base import BaseCommand
from accounts.models import User
from doctors.models import AvailabilitySlot
from appointments.models import Appointment


class Command(BaseCommand):
    """
    Seed appointments with the approval workflow.

    Creates a mix of:
        - requested (waiting for doctor)
        - accepted (confirmed)
        - rejected (declined by doctor)
        - completed (with notes)
        - no_show
        - cancelled
    """

    help = "Populate the database with dummy appointments."

    def handle(self, *args, **options):
        """Run the seeding logic."""
        self.stdout.write(self.style.WARNING("Seeding appointments..."))

        # Format: (patient_username, doctor_username, slot_index, status, notes)
        plans = [
            ('ravi',   'dr_sharma', 0, 'requested', ''),
            ('priya',  'dr_sharma', 1, 'accepted', ''),
            ('arjun',  'dr_patel',  0, 'requested', ''),
            ('sneha',  'dr_patel',  2, 'rejected', ''),
            ('vikram', 'dr_khan',   0, 'accepted', ''),
            ('ravi',   'dr_khan',   3, 'cancelled', ''),
        ]

        created_count = 0
        skipped_count = 0

        for patient_username, doctor_username, slot_idx, status, notes in plans:
            try:
                patient = User.objects.get(username=patient_username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Patient {patient_username} not found.")
                )
                continue

            # Get free slots for this doctor
            slots = list(
                AvailabilitySlot.objects.filter(
                    doctor__user__username=doctor_username,
                    is_booked=False
                ).order_by('date', 'start_time')
            )

            if slot_idx >= len(slots):
                self.stdout.write(
                    self.style.WARNING(f"  - Not enough free slots for {doctor_username}")
                )
                skipped_count += 1
                continue

            slot = slots[slot_idx]

            # Skip if slot already has an appointment
            if Appointment.objects.filter(slot=slot).exists():
                skipped_count += 1
                continue

            # Create appointment
            Appointment.objects.create(
                slot=slot,
                patient=patient,
                status=status,
                notes=notes,
            )

            # Book the slot only if status is accepted/completed/no_show
            if status in ['accepted', 'completed', 'no_show']:
                slot.is_booked = True
                slot.save()

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ {patient_username} → Dr. {doctor_username} [{status}]"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Appointments seeded. Created: {created_count}, Skipped: {skipped_count}"
            )
        )