"""
Views for the appointments app.
Handles booking, viewing, cancelling, and status updates.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from doctors.models import AvailabilitySlot, DoctorProfile
from .models import Appointment
from .serializers import AppointmentSerializer
from utils.responses import success_response, error_response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_appointment(request):
    """
    Allow a patient to book an available slot.

    Method: POST
    URL: /api/appointments/book/
    Auth: Required (patient only).
    Body: { slot: <slot_id> }

    Returns:
        201: Appointment created.
        400: Slot already booked / not found / invalid.
        403: If user is not a patient.
    """
    if not request.user.is_patient():
        return error_response(
            message="Only patients can book appointments.",
            status=403
        )

    slot_id = request.data.get('slot')
    if not slot_id:
        return error_response(message="Slot ID is required.", status=400)

    try:
        slot = AvailabilitySlot.objects.get(id=slot_id)
    except AvailabilitySlot.DoesNotExist:
        return error_response(message="Slot not found.", status=404)

    if slot.is_booked:
        return error_response(
            message="This slot is already booked.",
            status=400
        )

    # Create appointment
    appointment = Appointment.objects.create(
        slot=slot,
        patient=request.user,
        status='pending'
    )

    # Mark the slot as booked
    slot.is_booked = True
    slot.save()

    serializer = AppointmentSerializer(appointment)
    return success_response(
        data=serializer.data,
        message="Appointment booked successfully.",
        status=201
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_appointments(request):
    """
    Return all appointments booked by the logged-in patient.

    Method: GET
    URL: /api/my-appointments/
    Auth: Required (patient only).

    Returns:
        200: List of own appointments.
        403: If user is not a patient.
    """
    if not request.user.is_patient():
        return error_response(
            message="Only patients can view their appointments.",
            status=403
        )

    appointments = Appointment.objects.filter(patient=request.user)
    serializer = AppointmentSerializer(appointments, many=True)
    return success_response(
        data=serializer.data,
        message=f"{appointments.count()} appointments found.",
        status=200
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, appointment_id):
    """
    Allow a patient to cancel their own appointment.

    Method: PUT
    URL: /api/appointments/<id>/cancel/
    Auth: Required (appointment owner only).

    Returns:
        200: Appointment cancelled.
        400: Cannot cancel a completed/cancelled appointment.
        403: If not the owner.
        404: Appointment not found.
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return error_response(message="Appointment not found.", status=404)

    if appointment.patient != request.user:
        return error_response(
            message="You can only cancel your own appointments.",
            status=403
        )

    if appointment.status in ['completed', 'cancelled']:
        return error_response(
            message=f"Cannot cancel an appointment marked as '{appointment.status}'.",
            status=400
        )

    appointment.status = 'cancelled'
    appointment.save()

    # Free up the slot again
    slot = appointment.slot
    slot.is_booked = False
    slot.save()

    serializer = AppointmentSerializer(appointment)
    return success_response(
        data=serializer.data,
        message="Appointment cancelled.",
        status=200
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_appointments(request):
    """
    Return all appointments booked for the logged-in doctor.

    Method: GET
    URL: /api/doctor/appointments/
    Auth: Required (doctor only).

    Returns:
        200: List of appointments for this doctor.
        403: If user is not a doctor.
        400: If doctor has no profile.
    """
    if not request.user.is_doctor():
        return error_response(
            message="Only doctors can view their appointments.",
            status=403
        )

    try:
        doctor = DoctorProfile.objects.get(user=request.user)
    except DoctorProfile.DoesNotExist:
        return error_response(
            message="Please create your doctor profile first.",
            status=400
        )

    appointments = Appointment.objects.filter(slot__doctor=doctor)
    serializer = AppointmentSerializer(appointments, many=True)
    return success_response(
        data=serializer.data,
        message=f"{appointments.count()} appointments found.",
        status=200
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_appointment_status(request, appointment_id):
    """
    Allow a doctor to mark an appointment as completed or no_show.

    Method: PUT
    URL: /api/appointments/<id>/status/
    Auth: Required (appointment's doctor only).
    Body: { status: 'completed' | 'no_show' | 'pending' }

    Returns:
        200: Status updated.
        400: Invalid status.
        403: If not the doctor of this appointment.
        404: Appointment not found.
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return error_response(message="Appointment not found.", status=404)

    if appointment.slot.doctor.user != request.user:
        return error_response(
            message="You can only manage your own appointments.",
            status=403
        )

    new_status = request.data.get('status')
    if new_status not in ['pending', 'completed', 'no_show']:
        return error_response(
            message="Status must be pending, completed, or no_show.",
            status=400
        )

    appointment.status = new_status
    appointment.save()

    serializer = AppointmentSerializer(appointment)
    return success_response(
        data=serializer.data,
        message=f"Appointment marked as {new_status}.",
        status=200
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def add_appointment_notes(request, appointment_id):
    """
    Allow a doctor to add prescription notes to an appointment.

    Method: PUT
    URL: /api/appointments/<id>/notes/
    Auth: Required (appointment's doctor only).
    Body: { notes: "..." }

    Returns:
        200: Notes saved.
        403: If not the doctor of this appointment.
        404: Appointment not found.
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return error_response(message="Appointment not found.", status=404)

    if appointment.slot.doctor.user != request.user:
        return error_response(
            message="You can only add notes to your own appointments.",
            status=403
        )

    notes = request.data.get('notes', '').strip()
    if not notes:
        return error_response(message="Notes cannot be empty.", status=400)

    appointment.notes = notes
    appointment.save()

    serializer = AppointmentSerializer(appointment)
    return success_response(
        data=serializer.data,
        message="Notes saved.",
        status=200
    )


from django.shortcuts import render


def page_login(request):
    """Render login page."""
    return render(request, 'login.html')


def page_register(request):
    """Render register page."""
    return render(request, 'register.html')


def page_doctors(request):
    """Render doctors listing page."""
    return render(request, 'doctors.html')


def page_my_appointments(request):
    """Render patient's appointments page."""
    return render(request, 'my_appointments.html')


def page_doctor_dashboard(request):
    """Render doctor dashboard page."""
    return render(request, 'doctor_dashboard.html')