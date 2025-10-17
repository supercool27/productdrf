from functools import wraps
from rest_framework.exceptions import PermissionDenied


def customer_only_list(view_method):
    @wraps(view_method)
    def _wrapped(self, request, *args, **kwargs):
        user = request.user
        if user.is_staff:
            return view_method(self, request, *args, **kwargs)
        # If user has a related customer, ensure queryset is restricted to that customer
        if hasattr(user, "customers") and user.customers.exists():
            setattr(self, "_force_customer_id", user.customers.first().id)
            return view_method(self, request, *args, **kwargs)
        # No permission to list orders
        raise PermissionDenied("You do not have permission to view these orders.")

    return _wrapped


