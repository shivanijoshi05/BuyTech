from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def is_admin(user):
    return user.is_authenticated and user.user_type == 'Admin'

def admin_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if is_admin(request.user):
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied("You are not authorized to access this page.")
    
    return _wrapped_view
