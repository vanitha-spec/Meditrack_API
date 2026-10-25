"""
Serializers for the accounts app.
Handles user registration and login data validation.
"""

from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.

    Validates username, email, password, and role.
    Ensures password is write-only and hashed via set_password().
    """

    password = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text="Password must be at least 6 characters."
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')

    def validate_username(self, value):
        """
        Ensure the username is not already taken.

        Args:
            value (str): The username entered by the user.

        Returns:
            str: The validated username.

        Raises:
            ValidationError: If username already exists.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        """
        Ensure the email is not already registered.

        Args:
            value (str): The email entered by the user.

        Returns:
            str: The validated email.

        Raises:
            ValidationError: If email already exists.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate_role(self, value):
        """
        Ensure the role is one of the allowed values.

        Args:
            value (str): The role entered by the user.

        Returns:
            str: The validated role.

        Raises:
            ValidationError: If role is not 'doctor' or 'patient'.
        """
        if value not in ['doctor', 'patient']:
            raise serializers.ValidationError(
                "Role must be either 'doctor' or 'patient'."
            )
        return value

    def create(self, validated_data):
        """
        Create and return a new user with an encrypted password.

        Args:
            validated_data (dict): Cleaned data from the serializer.

        Returns:
            User: The newly created user instance.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data['role'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Accepts username and password and validates the credentials.
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate the username and password combination.

        Args:
            data (dict): Contains 'username' and 'password'.

        Returns:
            dict: The validated data including the User object.

        Raises:
            ValidationError: If credentials are invalid.
        """
        user = authenticate(
            username=data.get('username'),
            password=data.get('password')
        )
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is disabled.")

        data['user'] = user
        return data