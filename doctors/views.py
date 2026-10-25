"""
Views for the doctors app.
Handles doctor profile creation, listing and detail.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import DoctorProfile
from .serializers import DoctorProfileSerializer
from utils.responses import success_response, error_response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_profile(request):
    """
    Allow a doctor to create or update their profile.

    Method: POST
    URL: /api/doctors/profile/
    Auth: Required (doctor only).
    Body: { specialization, experience_years, consultation_fee, bio }

    Returns:
        200: Profile updated.
        201: Profile created.
        403: If user is not a doctor.
        400: Validation errors.
    """
    if not request.user.is_doctor():
        return error_response(
            message="Only doctors can create a profile.",
            status=403
        )

    # Check if a profile already exists for this doctor
    try:
        profile = DoctorProfile.objects.get(user=request.user)
        created = False
    except DoctorProfile.DoesNotExist:
        profile = None
        created = True

    serializer = DoctorProfileSerializer(
        profile,
        data=request.data,
        partial=not created
    )

    if not serializer.is_valid():
        return error_response(
            message="Invalid profile data.",
            status=400,
            errors=serializer.errors
        )

    serializer.save(user=request.user)

    return success_response(
        data=serializer.data,
        message="Profile created." if created else "Profile updated.",
        status=201 if created else 200
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_doctors(request):
    """
    Return a list of all doctors (public).

    Method: GET
    URL: /api/doctors/
    Auth: Not required.

    Returns:
        200: List of doctor profiles.
    """
    doctors = DoctorProfile.objects.all()
    serializer = DoctorProfileSerializer(doctors, many=True)
    return success_response(
        data=serializer.data,
        message=f"{doctors.count()} doctors found.",
        status=200
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def doctor_detail(request, doctor_id):
    """
    Return details of a single doctor.

    Method: GET
    URL: /api/doctors/<id>/
    Auth: Not required.

    Returns:
        200: Doctor details.
        404: Doctor not found.
    """
    try:
        doctor = DoctorProfile.objects.get(id=doctor_id)
    except DoctorProfile.DoesNotExist:
        return error_response(message="Doctor not found.", status=404)

    serializer = DoctorProfileSerializer(doctor)
    return success_response(data=serializer.data, status=200)


from .models import DoctorProfile, AvailabilitySlot
from .serializers import DoctorProfileSerializer, AvailabilitySlotSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_slot(request):
    """
    Allow a doctor to create an availability slot.

    Method: POST
    URL: /api/slots/
    Auth: Required (doctor only).
    Body: { date, start_time, end_time }

    Returns:
        201: Slot created.
        400: Validation errors.
        403: If user is not a doctor or has no profile.
    """
    if not request.user.is_doctor():
        return error_response(
            message="Only doctors can create slots.",
            status=403
        )

    # Get the doctor's profile
    try:
        doctor = DoctorProfile.objects.get(user=request.user)
    except DoctorProfile.DoesNotExist:
        return error_response(
            message="Please create your doctor profile first.",
            status=400
        )

    serializer = AvailabilitySlotSerializer(data=request.data)

    if not serializer.is_valid():
        return error_response(
            message="Invalid slot data.",
            status=400,
            errors=serializer.errors
        )

    serializer.save(doctor=doctor)
    return success_response(
        data=serializer.data,
        message="Slot created successfully.",
        status=201
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_slots(request):
    """
    Return available slots, optionally filtered by doctor.

    Method: GET
    URL: /api/slots/?doctor=<id>
    Auth: Not required.

    Returns:
        200: List of slots (unbooked by default).
    """
    doctor_id = request.GET.get('doctor')
    show_all = request.GET.get('all') == 'true'

    slots = AvailabilitySlot.objects.all()

    # Filter by doctor if provided
    if doctor_id:
        slots = slots.filter(doctor_id=doctor_id)

    # By default, only show unbooked slots
    if not show_all:
        slots = slots.filter(is_booked=False)

    serializer = AvailabilitySlotSerializer(slots, many=True)
    return success_response(
        data=serializer.data,
        message=f"{slots.count()} slots found.",
        status=200
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_slot(request, slot_id):
    """
    Allow a doctor to delete their own unbooked slot.

    Method: DELETE
    URL: /api/slots/<id>/
    Auth: Required (slot owner only).

    Returns:
        200: Slot deleted.
        400: If slot is already booked.
        403: If not the owner.
        404: Slot not found.
    """
    try:
        slot = AvailabilitySlot.objects.get(id=slot_id)
    except AvailabilitySlot.DoesNotExist:
        return error_response(message="Slot not found.", status=404)

    if slot.doctor.user != request.user:
        return error_response(
            message="You can only delete your own slots.",
            status=403
        )

    if slot.is_booked:
        return error_response(
            message="Cannot delete a slot that is already booked.",
            status=400
        )

    slot.delete()
    return success_response(message="Slot deleted successfully.", status=200)