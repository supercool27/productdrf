import time
from django.utils.deprecation import MiddlewareMixin
from .models import PlatformApiCall


class AuditLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        try:
            duration_ms = None
            if hasattr(request, "_start_time"):
                duration_ms = int((time.time() - request._start_time) * 1000)
            PlatformApiCall.objects.create(
                user=getattr(request, "user", None) if getattr(request, "user", None) and getattr(request, "user").is_authenticated else None,
                requested_url=getattr(request, "path", ""),
                requested_data=None,  # keep payload logging in view mixin only
                response_data={"status_code": getattr(response, "status_code", None), "duration_ms": duration_ms},
            )
        except Exception:
            pass
        return response


