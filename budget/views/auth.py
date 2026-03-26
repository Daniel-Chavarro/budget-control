"""Authentication views for budget app."""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse
from django.views.decorators.http import require_POST
from budget.forms import UserRegistrationForm


def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('budget:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'budget/auth/register.html', {'form': form})


def login_view(request):
    """User login view."""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):
                return redirect(next_url)
            return redirect(reverse('budget:dashboard'))
    else:
        form = AuthenticationForm()
    
    return render(request, 'budget/auth/login.html', {'form': form})


@require_POST
def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('budget:login')
