"""
Standard JSON response helpers used across the project.
Keeping responses consistent makes the API easier to consume.
"""

from rest_framework.response import Response


def success_response(data=None, message="Success", status=200):
    """
    Return a standard success JSON response.

    Args:
        data (any): The payload to return.
        message (str): A short success message.
        status (int): HTTP status code (default 200).

    Returns:
        Response: DRF Response with success=True.
    """
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=status,
    )


def error_response(message="Something went wrong", status=400, errors=None):
    """
    Return a standard error JSON response.

    Args:
        message (str): Human-readable error message.
        status (int): HTTP status code (default 400).
        errors (dict | None): Optional field-level errors.

    Returns:
        Response: DRF Response with success=False.
    """
    return Response(
        {
            "success": False,
            "message": message,
            "errors": errors or {},
        },
        status=status,
    )