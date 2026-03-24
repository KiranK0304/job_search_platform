from functools import wraps
from django.shortcuts import redirect


def seeker_required(view_func):
    """Only allow users with role='seeker'. Redirects others."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.profile.role != "seeker":
            return redirect("provider_dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


def provider_required(view_func):
    """Only allow users with role='provider'. Redirects others."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.profile.role != "provider":
            return redirect("seeker_dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper
