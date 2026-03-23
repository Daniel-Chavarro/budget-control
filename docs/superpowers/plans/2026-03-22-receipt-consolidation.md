# Receipt Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge ExpenseData and IncomeData into Receipt table to simplify data structure

**Architecture:** Add transaction fields (date, amount, category, counterparty, description, modified_by_user) directly to Receipt model. Update forms, views, and templates to use new unified structure.

**Tech Stack:** Django, SQLite, Python

---

### Task 1: Update Receipt Model with new fields

**Files:**
- Modify: `budget/models/receipt.py:30-96`

- [ ] **Step 1: Add new fields to Receipt model**

Add after `review_notes` field:
```python
# Transaction data (merged from ExpenseData and IncomeData)
date = models.DateField(null=True, blank=True)
amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
counterparty = models.CharField(max_length=200, blank=True, help_text="Vendor for expenses, payer for income")
category = models.ForeignKey(
    Category,
    on_delete=models.PROTECT,
    null=True,
    blank=True,
    related_name='transactions'
)
description = models.TextField(blank=True)
modified_by_user = models.BooleanField(default=False)
```

- [ ] **Step 2: Run check**

Run: `python manage.py check`
Expected: No errors

- [ ] **Step 3: Create migration**

Run: `python manage.py makemigrations budget --name add_transaction_fields_to_receipt`
Expected: Migration created

- [ ] **Step 4: Apply migration**

Run: `python manage.py migrate budget`
Expected: OK

---

### Task 2: Data Migration - Copy values from old tables

**Files:**
- Create: `budget/migrations/000X_migrate_data.py` (data migration)

- [ ] **Step 1: Create data migration script**

Create file `budget/migrations/0008_migrate_transaction_data.py`:
```python
from django.db import migrations

def migrate_expense_data(apps, schema_editor):
    Receipt = apps.get_model('budget', 'Receipt')
    ExpenseData = apps.get_model('budget', 'ExpenseData')
    
    for expense in ExpenseData.objects.select_related('receipt').all():
        receipt = expense.receipt
        receipt.date = expense.date
        receipt.amount = expense.amount
        receipt.counterparty = expense.vendor
        receipt.category = expense.category
        receipt.description = expense.description
        receipt.modified_by_user = expense.modified_by_user
        receipt.save()

def migrate_income_data(apps, schema_editor):
    Receipt = apps.get_model('budget', 'Receipt')
    IncomeData = apps.get_model('budget', 'IncomeData')
    
    for income in IncomeData.objects.select_related('receipt').all():
        receipt = income.receipt
        receipt.date = income.date
        receipt.amount = income.amount
        receipt.counterparty = income.payer
        receipt.category = income.category
        receipt.description = income.description
        receipt.modified_by_user = income.modified_by_user
        receipt.save()

def reverse_migration(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('budget', '0007_add_transaction_fields_to_receipt'),
    ]
    
    operations = [
        migrations.RunPython(migrate_expense_data, reverse_migration),
        migrations.RunPython(migrate_income_data, reverse_migration),
    ]
```

- [ ] **Step 2: Run data migration**

Run: `python manage.py migrate budget`
Expected: OK

---

### Task 3: Update Receipt Forms

**Files:**
- Modify: `budget/forms/receipt_forms.py` - Remove ExpenseDataForm and IncomeDataForm, create unified TransactionForm
- Modify: `budget/forms/__init__.py`

- [ ] **Step 1: Rewrite receipt_forms.py**

Replace contents with:
```python
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


class TransactionForm(forms.ModelForm):
    """Unified form for transaction data (income or expense)."""
    
    def __init__(self, *args, receipt_type='expense', **kwargs):
        super().__init__(*args, **kwargs)
        self.receipt_type = receipt_type
        self.fields['category'].queryset = Category.objects.filter(
            category_type=receipt_type,
            is_active=True
        ).order_by('name_es')
        self.fields['category'].empty_label = 'Seleccionar categoria'
        
        # Change label based on type
        if receipt_type == 'expense':
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
```

- [ ] **Step 2: Update __init__.py**

Modify: `budget/forms/__init__.py`

```python
"""Budget app forms."""
from .auth_forms import UserRegistrationForm
from .management_forms import UnitForm, UserUnitForm, UserCreateForm, CategoryForm
from .receipt_forms import ReceiptUploadForm, TransactionForm, get_category_by_name_es

__all__ = [
    'UserRegistrationForm',
    'UnitForm',
    'UserUnitForm',
    'UserCreateForm',
    'CategoryForm',
    'ReceiptUploadForm',
    'TransactionForm',
    'get_category_by_name_es',
]
```

- [ ] **Step 3: Run check**

Run: `python manage.py check`
Expected: No errors

---

### Task 4: Update Receipt Views

**Files:**
- Modify: `budget/views/receipts.py`

- [ ] **Step 1: Rewrite receipts.py**

Replace imports and update upload view:
```python
"""Receipt upload and management views."""
import base64
import logging

from PIL import Image
from django.shortcuts import render, redirect
from django.contrib import messages
from budget.decorators import any_authenticated_user
from budget.models import Receipt
from budget.forms import ReceiptUploadForm, TransactionForm, get_category_by_name_es
from budget.services import get_storage_service, get_ocr_service
from datetime import datetime

logger = logging.getLogger(__name__)

# ... keep existing imports and other views, just update receipt_upload_view
```

Update `receipt_upload_view` to use `TransactionForm` instead of `ExpenseDataForm`/`IncomeDataForm`:
- Replace all `expense_form` references with `transaction_form`
- Replace `ExpenseDataForm(request.POST, ...)` with `TransactionForm(request.POST, receipt_type=receipt_type, instance=receipt)`
- Replace `expense_form.save(commit=False)` with `transaction_form.save(commit=False)`
- Save directly to `receipt` object: `receipt.date = data.date; receipt.amount = data.amount; receipt.counterparty = data.counterparty; receipt.category = data.category; receipt.description = data.description; receipt.modified_by_user = True; receipt.save()`

- [ ] **Step 2: Run check**

Run: `python manage.py check`
Expected: No errors

---

### Task 5: Update Dashboard Views

**Files:**
- Modify: `budget/views/dashboard.py`

- [ ] **Step 1: Update dashboard.py**

Replace queries to use Receipt fields directly:
- Replace `ExpenseData.objects.filter(...)` with `Receipt.objects.filter(..., receipt_type='expense')`
- Replace `IncomeData.objects.filter(...)` with `Receipt.objects.filter(..., receipt_type='income')`
- Update template context variable names (no more `expense_data.amount`, use `receipt.amount`)

Key changes:
```python
# Instead of:
expense_data__amount, use: amount

# In tenant_dashboard:
month_total = Receipt.objects.filter(
    status='approved',
    receipt_type='income',
    uploaded_by=user,
    date__gte=this_month_start
).aggregate(total=Sum('amount'))['total'] or 0

# In admin_dashboard:
month_expenses = Receipt.objects.filter(
    status='approved',
    receipt_type='expense',
    date__gte=this_month_start
).aggregate(total=Sum('amount'))['total'] or 0
```

- [ ] **Step 2: Run check**

Run: `python manage.py check`
Expected: No errors

---

### Task 6: Update Reports View

**Files:**
- Modify: `budget/views/reports.py`

- [ ] **Step 1: Rewrite reports.py**

```python
"""Report views for budget app."""
from django.shortcuts import render
from django.db.models import Sum, Count
from budget.decorators import admin_required
from budget.models import Receipt, Category

@admin_required
def expense_report_view(request):
    """Detailed expense/income report with filtering."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category_id = request.GET.get('category', '')
    report_type = request.GET.get('type', 'all')
    
    expense_categories = Category.objects.filter(category_type='expense', is_active=True).order_by('name_es')
    income_categories = Category.objects.filter(category_type='income', is_active=True).order_by('name_es')
    
    receipts = Receipt.objects.filter(status='approved')
    
    if start_date:
        receipts = receipts.filter(date__gte=start_date)
    if end_date:
        receipts = receipts.filter(date__lte=end_date)
    
    expenses = receipts.filter(receipt_type='expense')
    incomes = receipts.filter(receipt_type='income')
    
    expense_category_totals = expenses.values('category__name', 'category__name_es').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    income_category_totals = incomes.values('category__name', 'category__name_es').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_incomes = incomes.aggregate(total=Sum('amount'))['total'] or 0
    balance = total_incomes - total_expenses
    
    context = {
        'expenses': expenses.select_related('uploaded_by', 'category')[:100] if report_type in ['all', 'expense'] else [],
        'incomes': incomes.select_related('uploaded_by', 'category')[:100] if report_type in ['all', 'income'] else [],
        'total_expenses': total_expenses,
        'total_incomes': total_incomes,
        'balance': balance,
        'expense_category_totals': expense_category_totals,
        'income_category_totals': income_category_totals,
        'expense_categories': expense_categories,
        'income_categories': income_categories,
        'start_date': start_date,
        'end_date': end_date,
        'selected_type': report_type,
        'selected_category': category_id,
    }
    
    return render(request, 'budget/reports/expense_report.html', context)
```

- [ ] **Step 2: Run check**

Run: `python manage.py check`
Expected: No errors

---

### Task 7: Update Review View

**Files:**
- Modify: `budget/views/review.py`

- [ ] **Step 1: Update review.py**

- Replace `expense_form = ExpenseDataForm(...)` with `transaction_form = TransactionForm(instance=receipt, receipt_type=receipt.receipt_type)`
- Update saving logic to use receipt directly
- Update template context: use `receipt.amount`, `receipt.counterparty`, etc.

- [ ] **Step 2: Run check**

Run: `python manage.py check`
Expected: No errors

---

### Task 8: Update Templates

**Files:**
- Modify: `budget/templates/budget/receipts/upload.html`
- Modify: `budget/templates/budget/receipts/list.html`
- Modify: `budget/templates/budget/dashboard/admin.html`
- Modify: `budget/templates/budget/dashboard/tenant.html`
- Modify: `budget/templates/budget/reports/expense_report.html`
- Modify: `budget/templates/budget/review/detail.html`

- [ ] **Step 1: Update upload.html**

Replace `expense_form` with `transaction_form` in form rendering logic

- [ ] **Step 2: Update list.html**

Replace `receipt.expense_data.amount`, `receipt.expense_data.vendor` with `receipt.amount`, `receipt.counterparty`

- [ ] **Step 3: Update dashboard templates**

Update context variables: use receipt.amount, receipt.counterparty, receipt.category directly

- [ ] **Step 4: Run check**

Run: `python manage.py check`
Expected: No errors

---

### Task 9: Delete old models (optional - after verification)

**Files:**
- Modify: `budget/models/receipt.py` - Remove ExpenseData and IncomeData classes
- Modify: `budget/models/__init__.py` - Remove exports

- [ ] **Step 1: Remove old models**

After all tests pass and verifying data is correct, remove the old model classes.

- [ ] **Step 2: Run final check**

Run: `python manage.py check`
Run: `python manage.py test`
Expected: All pass

---

### Task 10: Final Testing

**Verification:**
- [ ] Upload expense receipt - works
- [ ] Upload income receipt - works
- [ ] Dashboard shows correct totals
- [ ] Reports show correct breakdown
- [ ] Review/approve flow works

Run comprehensive test:
```bash
python manage.py test
```

---

## Execution Options

**Plan complete and saved to `docs/superpowers/plans/2026-03-22-receipt-consolidation.md`. Two execution options:**

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**