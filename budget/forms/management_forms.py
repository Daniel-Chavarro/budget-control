"""Management forms for users and categories."""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from budget.models import UserProfile, Category


class UserCreateForm(forms.ModelForm):
    """Form for admin to create users (tenant/unlinked_user)."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Contraseña'
    )
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar contraseña'
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Rol del Usuario',
        required=True
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')
        
        if password and password_confirmation:
            if password != password_confirmation:
                raise forms.ValidationError({'password_confirmation': 'Las contraseñas no coinciden.'})
            
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as e:
                raise forms.ValidationError({'password': e.messages})
        
        return cleaned_data
    
    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role not in ['tenant', 'unlinked_user']:
            raise forms.ValidationError('Rol inválido.')
        return role
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'role': self.cleaned_data.get('role', 'tenant')}
            )
        return user


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'category_type', 'is_active']
        labels = {
            'name': 'Nombre',
            'category_type': 'Tipo',
            'is_active': 'Activo',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category_type': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
