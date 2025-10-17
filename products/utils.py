from typing import Any
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc: Exception, context: dict[str, Any]):
    response = exception_handler(exc, context)
    if response is None:
        return Response({"code": "server_error", "message": str(exc), "field_errors": None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    data = {
        "code": "validation_error" if response.status_code == 400 else "error",
        "message": response.data if isinstance(response.data, str) else "Validation failed" if response.status_code == 400 else "Request failed",
        "field_errors": response.data if isinstance(response.data, dict) else None,
    }
    return Response(data, status=response.status_code)


