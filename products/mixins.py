from __future__ import annotations

from typing import Any

from django.utils.timezone import now
from rest_framework.request import Request
from rest_framework.response import Response

from .models import PlatformApiCall


class PlatformApiCallMixin:
    def finalize_response(self, request: Request, response: Response, *args: Any, **kwargs: Any) -> Response:
        try:
            PlatformApiCall.objects.create(
                user=getattr(request, "user", None) if getattr(request, "user", None) and getattr(request, "user").is_authenticated else None,
                requested_url=request.get_full_path(),
                requested_data=getattr(request, "data", None),
                response_data=getattr(response, "data", None) if hasattr(response, "data") else None,
            )
        except Exception:  # logging must never break API response
            pass
        return super().finalize_response(request, response, *args, **kwargs)


