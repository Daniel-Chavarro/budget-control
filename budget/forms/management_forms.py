"""Management forms for units and users."""
from django import forms
from budget.models import Unit, UserUnit


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
