"""Receipt-related forms."""
from django import forms
from budget.models import Receipt, ExpenseData, IncomeData, Category
from django.contrib.auth.models import User


class ReceiptUploadForm(forms.Form):
    """Form for uploading receipt file."""
    
    receipt_file = forms.FileField(
        label='Imagen del comprobante',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,application/pdf'
        }),
        help_text='Maximo: 10MB. Formatos: JPG, PNG, PDF'
    )
    
    receipt_type = forms.ChoiceField(
        label='Tipo de comprobante',
        choices=Receipt.RECEIPT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='expense'
    )
    
    upload_as_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Solo admin: Subir a nombre de otro usuario'
    )
    
    def clean_receipt_file(self):
        """Validate file size and type."""
        file = self.cleaned_data.get('receipt_file')
        
        if file:
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede exceder 10MB.')
            
            allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
            if file.content_type not in allowed_types:
                raise forms.ValidationError('Solo se permiten archivos JPG, PNG y PDF.')
        
        return file


def get_category_by_name_es(name: str, category_type: str = 'expense'):
    """Helper to get Category by Spanish name for OCR mapping."""
    if not name:
        return None
    try:
        return Category.objects.get(name_es__iexact=name, category_type=category_type, is_active=True)
    except Category.DoesNotExist:
        return None


class ExpenseDataForm(forms.ModelForm):
    """Form for editing expense data extracted from OCR."""
    
    def __init__(self, *args, category_type='expense', **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(
            category_type=category_type,
            is_active=True
        ).order_by('name_es')
        self.fields['category'].empty_label = 'Seleccionar categoria'
    
    class Meta:
        model = ExpenseData
        fields = ['date', 'amount', 'vendor', 'category', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_amount(self):
        """Validate amount is positive."""
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError('El monto debe ser positivo.')
        return amount


class IncomeDataForm(forms.ModelForm):
    """Form for editing income data extracted from receipt."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(
            category_type='income',
            is_active=True
        ).order_by('name_es')
        self.fields['category'].empty_label = 'Seleccionar categoria'
    
    class Meta:
        model = IncomeData
        fields = ['date', 'amount', 'payer', 'category', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payer': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_amount(self):
        """Validate amount is positive."""
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError('El monto debe ser positivo.')
        return amount
