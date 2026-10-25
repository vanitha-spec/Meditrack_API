"""
Management command to seed dummy users (doctors and patients).

Usage:
    python manage.py seed_users
"""

from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    """
    Seed the database with dummy doctors and patients.

    Creates:
        - 3 doctors
        - 5 patients
        - 1 admin (superuser)
    """

    help = "Populate the database with dummy users (doctors + patients)."

    def handle(self, *args, **options):
        """Run the seeding logic."""
        self.stdout.write(self.style.WARNING("Seeding users..."))

        # ---------- Admin ----------
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@meditrack.com',
                'role': 'patient',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin1234')
            admin.save()
            self.stdout.write(self.style.SUCCESS("  ✓ Admin created (admin / admin1234)"))
        else:
            self.stdout.write("  - Admin already exists")

        # ---------- Doctors ----------
        doctors = [
            {'username': 'dr_sharma', 'email': 'sharma@meditrack.com',
             'specialization': 'Cardiologist'},
            {'username': 'dr_patel', 'email': 'patel@meditrack.com',
             'specialization': 'Dermatologist'},
            {'username': 'dr_khan', 'email': 'khan@meditrack.com',
             'specialization': 'Pediatrician'},
        ]

        for d in doctors:
            user, created = User.objects.get_or_create(
                username=d['username'],
                defaults={'email': d['email'], 'role': 'doctor'}
            )
            if created:
                user.set_password('doctor1234')
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Doctor: {d['username']} / doctor1234 ({d['specialization']})"
                    )
                )
            else:
                self.stdout.write(f"  - Doctor {d['username']} already exists")

        # ---------- Patients ----------
        patients = [
            {'username': 'ravi', 'email': 'ravi@meditrack.com'},
            {'username': 'priya', 'email': 'priya@meditrack.com'},
            {'username': 'arjun', 'email': 'arjun@meditrack.com'},
            {'username': 'sneha', 'email': 'sneha@meditrack.com'},
            {'username': 'vikram', 'email': 'vikram@meditrack.com'},
        ]

        for p in patients:
            user, created = User.objects.get_or_create(
                username=p['username'],
                defaults={'email': p['email'], 'role': 'patient'}
            )
            if created:
                user.set_password('patient1234')
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Patient: {p['username']} / patient1234")
                )
            else:
                self.stdout.write(f"  - Patient {p['username']} already exists")

        self.stdout.write(self.style.SUCCESS("\n✅ Users seeded successfully."))
        self.stdout.write("\n📋 Login credentials:")
        self.stdout.write("   Admin:   admin / admin1234")
        self.stdout.write("   Doctor:  dr_sharma / doctor1234")
        self.stdout.write("   Patient: ravi / patient1234")