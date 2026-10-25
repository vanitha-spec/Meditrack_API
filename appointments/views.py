"""
Views for the appointments app.
Handles booking, viewing, cancelling, and status updates.

Workflow:
    1. Patient requests a slot → status = 'requested'
    2. Doctor approves → status = 'accepted' (slot marked booked)
    3. Doctor rejects → status = 'rejected' (slot remains free)
    4. After consultation → 'completed' or 'no_show'
    5. Patient can cancel before/after acceptance
"""

from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from doctors.models import AvailabilitySlot, DoctorProfile
from .models import Appointment
from .serializers import AppointmentSerializer
from utils.responses import success_response, error_response


# =============================================================
# PATIENT ENDPOINTS
# =============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_appointment(request):
    """
    Allow a patient to REQUEST an appointment.

    The slot is NOT marked booked until the doctor accepts.
    Status starts as 'requested'.

    Method: POST
    URL: /api/appointments/book/
    Auth: Required (patient only).
    Body: { slot: <slot_id> }

    Returns:
        201: Request created.
        400: Slot already booked / already requested.
        403: If user is not a patient.
        404: Slot not found.
    """
    if not request.user.is_patient():
        return error_response(
            message="Only patients can request appointments.",
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

    # Block duplicate requests for the same slot (unless previous was rejected)
    existing = Appointment.objects.filter(slot=slot).exclude(status='rejected').first()
    if existing:
        return error_response(
            message="This slot already has a pending or accepted request.",
            status=400
        )

    appointment = Appointment.objects.create(
        slot=slot,
        patient=request.user,
        status='requested'
    )

    serializer = AppointmentSerializer(appointment)
    return success_response(
        data=serializer.data,
        message="Appointment requested. Waiting for doctor approval.",
        status=201
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_appointments(request):
    """
    Return all appointments requested by the logged-in patient.

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

    Allowed states: 'requested' or 'accepted'.
    If it was accepted, the slot is freed again.

    Method: PUT
    URL: /api/appointments/<id>/cancel/
    Auth: Required (appointment owner only).

    Returns:
        200: Cancelled.
        400: Cannot cancel in current state.
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

    if appointment.status not in ['requested', 'accepted']:
        return error_response(
            message=f"Cannot cancel an appointment marked as '{appointment.status}'.",
            status=400
        )

    # If it was accepted, free the slot
    if appointment.status == 'accepted':
        slot = appointment.slot
        slot.is_booked = False
        slot.save()

    appointment.status = 'cancelled'
    appointment.save()

    serializer = AppointmentSerializer(appointment)
    return success_response(
        data=serializer.data,
        message="Appointment cancelled.",
        status=200
    )


# =============================================================
# DOCTOR ENDPOINTS
# =============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_appointments(request):
    """
    Return all appointments for the logged-in doctor.

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
def approve_appointment(request, appointment_id):
    """
    Allow a doctor to ACCEPT a requested appointment.

    On acceptance:
        - Appointment status → 'accepted'
        - Slot is marked as booked

    Method: PUT
    URL: /api/appointments/<id>/approve/
    Auth: Required (slot's doctor only).

    Returns:
        200: Accepted.
        400: If not in 'requested' state.
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

    if appointment.status != 'requested':
        return error_response(
            message=f"Cannot approve an appointment with status '{appointment.status}'.",
            status=400
        )

    appointment.status = 'accepted'
    appointment.save()

    # Mark slot as booked
    slot = appointment.slot
    slot.is_booked = True
    slot.save()

    serializer = AppointmentSerializer(appointment)
    return success_response(
        data=serializer.data,
        message="Appointment accepted. Slot is now booked.",
        status=200
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def reject_appointment(request, appointment_id):
    """
    Allow a doctor to REJECT a requested appointment.

    On rejection:
        - Appointment status → 'rejected'
        - Slot remains free for other patients

    Method: PUT
    URL: /api/appointments/<id>/reject/
    Auth: Required (slot's doctor only).

    Returns:
        200: Rejected.
        400: If not in 'requested' state.
        403: If not the doctor.
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

    if appointment.status != 'requested':
        return error_response(
            message=f"Cannot reject an appointment with status '{appointment.status}'.",
            status=400
        )

    appointment.status = 'rejected'
    appointment.save()

    # Slot stays free — no change to is_booked

    serializer = AppointmentSerializer(appointment)
    return success_response(
        data=serializer.data,
        message="Appointment rejected.",
        status=200
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_appointment_status(request, appointment_id):
    """
    Allow a doctor to mark an ACCEPTED appointment as
    'completed' or 'no_show'.

    Method: PUT
    URL: /api/appointments/<id>/status/
    Auth: Required (appointment's doctor only).
    Body: { status: 'completed' | 'no_show' }

    Returns:
        200: Status updated.
        400: Invalid status or wrong current state.
        403: If not the doctor.
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

    if appointment.status != 'accepted':
        return error_response(
            message="Only accepted appointments can be marked completed or no_show.",
            status=400
        )

    new_status = request.data.get('status')
    if new_status not in ['completed', 'no_show']:
        return error_response(
            message="Status must be 'completed' or 'no_show'.",
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
        400: Empty notes.
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


# =============================================================
# PAGE VIEWS (render HTML templates)
# =============================================================

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