"""Account editing forms."""
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class AccountForm(forms.Form):
    """Form for editing user account details."""
    
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            existing = User.objects.filter(username=username)
            if self.user:
                existing = existing.exclude(pk=self.user.pk)
            if existing.exists():
                raise ValidationError('A user with that username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            existing = User.objects.filter(email=email)
            if self.user:
                existing = existing.exclude(pk=self.user.pk)
            if existing.exists():
                raise ValidationError('A user with that email already exists.')
        return email


class PasswordChangeForm(forms.Form):
    """Form for changing user password."""
    
    current_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True,
        min_length=8,
        max_length=128
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        current = self.cleaned_data.get('current_password')
        if current and self.user:
            if not self.user.check_password(current):
                raise ValidationError('Current password is incorrect.')
        return current
    
    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if new_password and self.user:
            if self.user.check_password(new_password):
                raise ValidationError('New password must be different from current password.')
        return new_password
    
    def clean(self):
        cleaned = super().clean()
        new_password = cleaned.get('new_password')
        confirm_password = cleaned.get('confirm_password')
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError('Passwords do not match.')
        return cleaned
