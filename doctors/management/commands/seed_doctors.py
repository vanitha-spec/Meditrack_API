"""
Management command to seed DoctorProfiles and AvailabilitySlots.

Usage:
    python manage.py seed_doctors
"""

from datetime import date, time, timedelta

from django.core.management.base import BaseCommand
from accounts.models import User
from doctors.models import DoctorProfile, AvailabilitySlot


class Command(BaseCommand):
    """
    Seed doctor profiles and availability slots.

    Creates:
        - 3 doctor profiles (with specializations)
        - 6 slots per doctor (starting tomorrow)
    """

    help = "Populate the database with dummy doctor profiles and slots."

    def handle(self, *args, **options):
        """Run the seeding logic."""
        self.stdout.write(self.style.WARNING("Seeding doctor profiles..."))

        # ---------- Doctor Profiles ----------
        profile_data = {
            'dr_sharma': {
                'specialization': 'Cardiologist',
                'experience_years': 12,
                'consultation_fee': 800,
                'bio': 'Senior cardiologist with 12 years of experience in interventional cardiology.',
            },
            'dr_patel': {
                'specialization': 'Dermatologist',
                'experience_years': 6,
                'consultation_fee': 500,
                'bio': 'Dermatologist specializing in acne treatment and cosmetic procedures.',
            },
            'dr_khan': {
                'specialization': 'Pediatrician',
                'experience_years': 9,
                'consultation_fee': 600,
                'bio': 'Pediatrician with 9 years of experience caring for infants and children.',
            },
        }

        for username, data in profile_data.items():
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ User {username} not found. Run seed_users first.")
                )
                continue

            profile, created = DoctorProfile.objects.get_or_create(
                user=user,
                defaults=data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Profile: {username} ({data['specialization']})"
                    )
                )
            else:
                self.stdout.write(f"  - Profile for {username} already exists")

        # ---------- Slots ----------
        self.stdout.write(self.style.WARNING("\nSeeding availability slots..."))

        today = date.today()
        slot_times = [
            (time(10, 0), time(10, 30)),
            (time(11, 0), time(11, 30)),
            (time(14, 0), time(14, 30)),
            (time(15, 0), time(15, 30)),
        ]

        for username in profile_data.keys():
            try:
                doctor = DoctorProfile.objects.get(user__username=username)
            except DoctorProfile.DoesNotExist:
                continue

            created_count = 0
            # Create slots for next 2 days
            for offset in [1, 2]:
                slot_date = today + timedelta(days=offset)
                for start, end in slot_times:
                    slot, created = AvailabilitySlot.objects.get_or_create(
                        doctor=doctor,
                        date=slot_date,
                        start_time=start,
                        defaults={'end_time': end}
                    )
                    if created:
                        created_count += 1

            self.stdout.write(
                self.style.SUCCESS(f"  ✓ {created_count} slots added for {username}")
            )

        self.stdout.write(self.style.SUCCESS("\n✅ Doctor profiles + slots seeded."))