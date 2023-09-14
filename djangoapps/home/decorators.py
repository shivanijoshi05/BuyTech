from django.core.exceptions import PermissionDenied

def is_admin(user):
    return user.is_authenticated and user.user_type == 'Admin'

def admin_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is product admin using the custom is_admin function
        if is_admin(request.user):
            return view_func(request, *args, **kwargs)
        else:
            # If the user is not product admin, raise a PermissionDenied exception
            raise PermissionDenied("You are not authorized to access this page.")
    return _wrapped_view
