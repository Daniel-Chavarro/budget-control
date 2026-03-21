"""Budget app views."""
from django.shortcuts import render


def dashboard_view(request):
    """Temporary dashboard placeholder."""
    return render(request, 'budget/dashboard/index.html')


from .auth import register_view, login_view, logout_view

__all__ = ['register_view', 'login_view', 'logout_view', 'dashboard_view']
