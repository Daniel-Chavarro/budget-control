"""Management forms for units and users."""
from django import forms
from django.contrib.auth.models import User
from budget.models import Unit, UserUnit, UserProfile


class UnitForm(forms.ModelForm):
    """Form for creating/editing units."""
    
    class Meta:
        model = Unit
        fields = ['type', 'identifier', 'status', 'monthly_fee']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'identifier': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'monthly_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class UserUnitForm(forms.ModelForm):
    """Form for assigning users to units."""
    
    class Meta:
        model = UserUnit
        fields = ['user', 'unit', 'role_in_unit', 'start_date', 'end_date']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'role_in_unit': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class UserCreateForm(forms.ModelForm):
    """Form for admin to create users (tenant/unlinked_user)."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Password'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
