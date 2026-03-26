"""Account settings views."""
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from budget.forms import AccountForm, PasswordChangeForm


@login_required
def account_settings_view(request):
    """Display and handle account settings form."""
    initial_data = {
        'username': request.user.username,
        'email': request.user.email,
        'phone': getattr(request.user.userprofile, 'phone', '') if hasattr(request.user, 'userprofile') else '',
    }
    account_form = AccountForm(initial=initial_data, user=request.user)
    password_form = PasswordChangeForm(user=request.user)
    
    if request.method == 'POST':
        if 'username' in request.POST or 'email' in request.POST:
            account_form = AccountForm(request.POST, user=request.user)
            if account_form.is_valid():
                request.user.username = account_form.cleaned_data['username']
                request.user.email = account_form.cleaned_data['email']
                request.user.save()
                
                if hasattr(request.user, 'userprofile'):
                    request.user.userprofile.phone = account_form.cleaned_data.get('phone', '')
                    request.user.userprofile.save()
                
                messages.success(request, 'Account details updated successfully.')
                return redirect('budget:account_settings')
        elif 'current_password' in request.POST:
            password_form = PasswordChangeForm(request.POST, user=request.user)
            if password_form.is_valid():
                request.user.set_password(password_form.cleaned_data['new_password'])
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully.')
                return redirect('budget:account_settings')
    
    return render(request, 'budget/account/account_settings.html', {
        'account_form': account_form,
        'password_form': password_form,
    })
