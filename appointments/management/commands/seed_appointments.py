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
    Seed appointments.

    Creates a mix of:
        - pending appointments (upcoming)
        - completed appointments (with notes)
        - cancelled appointments
        - no_show appointments
    """

    help = "Populate the database with dummy appointments."

    def handle(self, *args, **options):
        """Run the seeding logic."""
        self.stdout.write(self.style.WARNING("Seeding appointments..."))

        # Format: (patient_username, doctor_username, slot_index, status, notes)
        plans = [
            ('ravi', 'dr_sharma', 0, 'pending', ''),
            ('priya', 'dr_sharma', 1, 'completed',
             'Mild hypertension detected. Prescribed Amlodipine 5mg once daily.'),
            ('arjun', 'dr_patel', 0, 'pending', ''),
            ('sneha', 'dr_patel', 2, 'no_show', ''),
            ('vikram', 'dr_khan', 0, 'completed',
             'Routine checkup. Child is healthy. Advised regular vitamin D.'),
            ('ravi', 'dr_khan', 3, 'cancelled', ''),
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

            try:
                slots = list(
                    AvailabilitySlot.objects.filter(
                        doctor__user__username=doctor_username,
                        is_booked=False
                    ).order_by('date', 'start_time')
                )
            except Exception:
                continue

            if slot_idx >= len(slots):
                self.stdout.write(
                    self.style.WARNING(f"  - Not enough free slots for {doctor_username}")
                )
                skipped_count += 1
                continue

            slot = slots[slot_idx]

            # Check if a slot already has an appointment
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

            # Slot is booked unless cancelled
            if status != 'cancelled':
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