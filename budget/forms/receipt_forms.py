"""Receipt-related forms."""
from django import forms
from budget.models import Receipt, Category
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
        initial='gasto',
        required=False
    )
    
    upload_as_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Solo admin: Subir a nombre de otro usuario'
    )
    
    def clean_receipt_type(self):
        """Return default if not provided."""
        return self.cleaned_data.get('receipt_type') or 'ingreso'
    
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


def get_category_by_name(name: str, category_type: str = 'gasto'):
    """Helper to get Category by Spanish name for OCR mapping."""
    if not name:
        return None
    try:
        return Category.objects.get(name__iexact=name, category_type=category_type, is_active=True)
    except Category.DoesNotExist:
        return None


class TransactionForm(forms.ModelForm):
    """Unified form for transaction data (income or expense)."""
    
    def __init__(self, *args, receipt_type='gasto', **kwargs):
        super().__init__(*args, **kwargs)
        self.receipt_type = receipt_type
        self.fields['category'].queryset = Category.objects.filter(
            category_type=receipt_type,
            is_active=True
        ).order_by('name')
        self.fields['category'].empty_label = 'Seleccionar categoria'
        
        if receipt_type == 'gasto':
            self.fields['counterparty'].label = 'Proveedor'
        else:
            self.fields['counterparty'].label = 'Pagador'
    
    class Meta:
        model = Receipt
        fields = ['date', 'amount', 'counterparty', 'category', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'counterparty': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_amount(self):
        """Validate amount is positive."""
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError('El monto debe ser positivo.')
        return amount