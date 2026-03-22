"""Receipt-related forms."""
from django import forms
from budget.models import Receipt, ExpenseData
from django.contrib.auth.models import User


class ReceiptUploadForm(forms.Form):
    """Form for uploading receipt file."""
    
    receipt_file = forms.FileField(
        label='Receipt Image/PDF',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,application/pdf'
        }),
        help_text='Max size: 10MB. Formats: JPG, PNG, PDF'
    )
    
    upload_as_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Admin only: Upload on behalf of another user'
    )
    
    def clean_receipt_file(self):
        """Validate file size and type."""
        file = self.cleaned_data.get('receipt_file')
        
        if file:
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size cannot exceed 10MB.')
            
            allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
            if file.content_type not in allowed_types:
                raise forms.ValidationError('Only JPG, PNG, and PDF files are allowed.')
        
        return file


class ExpenseDataForm(forms.ModelForm):
    """Form for editing expense data extracted from OCR."""
    
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
            raise forms.ValidationError('Amount must be positive.')
        return amount
