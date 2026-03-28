"""Custom decorators for budget app."""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def _add_message(request, level, message):
    """Add a message if messages framework is available."""
    try:
        messages.add_message(request, level, message)
    except (AttributeError, Exception):
        pass


def rate_limit(requests_per_minute=5, key_prefix='rate_limit'):
    """
    Rate limiting decorator using Django's cache.
    
    Args:
        requests_per_minute: Maximum requests allowed per minute
        key_prefix: Cache key prefix for this rate limit
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            user_id = request.user.id
            cache_key = f"{key_prefix}:{user_id}"
            
            request_count = cache.get(cache_key, 0)
            
            if request_count >= requests_per_minute:
                logger.warning(f"[RATE LIMIT] User {user_id} exceeded rate limit ({requests_per_minute}/min)")
                _add_message(
                    request, 
                    messages.WARNING, 
                    f'Demasiadas solicitudes. Intenta de nuevo en un minuto. (Límite: {requests_per_minute}/min)'
                )
                return HttpResponse('Too many requests', status=429)
            
            cache.set(cache_key, request_count + 1, 60)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


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
            return HttpResponseForbidden()
    
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
            return HttpResponseForbidden()
    
    return wrapper


def any_authenticated_user(view_func):
    """Decorator for views accessible to any authenticated user."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return wrapper
