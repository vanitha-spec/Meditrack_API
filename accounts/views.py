"""
Views for the accounts app.
Handles user registration and login endpoints.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer
from utils.responses import success_response, error_response


def get_tokens_for_user(user):
    """
    Generate JWT access and refresh tokens for a user.

    Args:
        user (User): The authenticated user instance.

    Returns:
        dict: Contains 'refresh' and 'access' token strings.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user (doctor or patient).

    Method: POST
    URL: /api/register/
    Body: { username, email, password, role }

    Returns:
        201: User created successfully with JWT tokens.
        400: Validation errors.
    """
    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return error_response(
            message="Registration failed.",
            status=400,
            errors=serializer.errors
        )

    user = serializer.save()
    tokens = get_tokens_for_user(user)

    return success_response(
        data={
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
            },
            'tokens': tokens,
        },
        message="User registered successfully.",
        status=201
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Log in an existing user and return JWT tokens.

    Method: POST
    URL: /api/login/
    Body: { username, password }

    Returns:
        200: Login successful with JWT tokens.
        400: Invalid credentials.
    """
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        return error_response(
            message="Login failed.",
            status=400,
            errors=serializer.errors
        )

    user = serializer.validated_data['user']
    tokens = get_tokens_for_user(user)

    return success_response(
        data={
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
            },
            'tokens': tokens,
        },
        message="Login successful.",
        status=200
    )