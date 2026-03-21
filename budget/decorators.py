"""Custom decorators for budget app."""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def _add_message(request, level, message):
    """Add a message if messages framework is available."""
    try:
        messages.add_message(request, level, message)
    except (AttributeError, Exception):
        pass


def admin_required(view_func):
    """Decorator to restrict view to admin users only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'userprofile'):
            _add_message(request, messages.ERROR, 'User profile not found.')
            return redirect('budget:login')
        
        if request.user.userprofile.is_admin:
            return view_func(request, *args, **kwargs)
        else:
            _add_message(request, messages.ERROR, 'Admin access required.')
            return HttpResponseForbidden('Admin access required')
    
    return wrapper


def tenant_or_admin_required(view_func):
    """Decorator to restrict view to tenant or admin users."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'userprofile'):
            _add_message(request, messages.ERROR, 'User profile not found.')
            return redirect('budget:login')
        
        profile = request.user.userprofile
        if profile.is_admin or profile.is_tenant:
            return view_func(request, *args, **kwargs)
        else:
            _add_message(request, messages.ERROR, 'Insufficient permissions.')
            return HttpResponseForbidden('Tenant or admin access required')
    
    return wrapper


def any_authenticated_user(view_func):
    """Decorator for views accessible to any authenticated user."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return wrapper
