# Receipt Upload & OCR Processing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement receipt upload workflow with OCR extraction, allowing tenants to upload receipts and admins to upload on behalf of users.

**Architecture:** Django models for Receipt and ExpenseData, HTMX for async file upload/preview, integration with OCR and Storage services.

**Tech Stack:** Django 6.0, HTMX, Bootstrap 5, OCR Service, Storage Service

---

## Task 1: Create Receipt and ExpenseData Models

**Files:**
- Create: `budget/models/receipt.py`
- Modify: `budget/models/__init__.py`
- Create: `budget/tests/test_receipt_models.py`

- [ ] **Step 1: Write failing tests**

Create `budget/tests/test_receipt_models.py`:

```python
"""Test suite for receipt models."""
from django.test import TestCase
from django.contrib.auth.models import User
from budget.models import Receipt, ExpenseData
from decimal import Decimal
from datetime import date


class TestReceiptModel(TestCase):
    """Test Receipt model."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='tenant', password='pass')
    
    def test_create_receipt(self):
        """Test creating receipt."""
        receipt = Receipt.objects.create(
            uploaded_by=self.user,
            original_file_url='https://example.com/file.jpg',
            file_name='receipt_001.jpg',
            status='pending_review'
        )
        assert receipt.uploaded_by == self.user
        assert receipt.status == 'pending_review'
        assert receipt.is_pending
        assert str(receipt) == f'Receipt receipt_001.jpg by tenant'


class TestExpenseDataModel(TestCase):
    """Test ExpenseData model."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='tenant', password='pass')
        self.receipt = Receipt.objects.create(
            uploaded_by=self.user,
            original_file_url='https://example.com/file.jpg',
            file_name='receipt.jpg'
        )
    
    def test_create_expense_data(self):
        """Test creating expense data."""
        expense = ExpenseData.objects.create(
            receipt=self.receipt,
            date=date.today(),
            amount=Decimal('99.99'),
            vendor='Test Vendor',
            category='utilities',
            description='Electric bill'
        )
        assert expense.amount == Decimal('99.99')
        assert expense.vendor == 'Test Vendor'
        assert not expense.modified_by_user
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest budget/tests/test_receipt_models.py -v
```

Expected: FAIL - models not defined

- [ ] **Step 3: Implement Receipt and ExpenseData models**

Create `budget/models/receipt.py`:

```python
"""Receipt-related models for budget app."""
from django.db import models
from django.contrib.auth.models import User


class Receipt(models.Model):
    """Uploaded receipt record."""
    
    STATUS_CHOICES = [
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_receipts'
    )
    original_file_url = models.URLField(max_length=500)
    file_name = models.CharField(max_length=255)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_review'
    )
    
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_receipts'
    )
    review_timestamp = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'receipts'
        verbose_name = 'Receipt'
        verbose_name_plural = 'Receipts'
        ordering = ['-upload_timestamp']
    
    def __str__(self):
        return f'Receipt {self.file_name} by {self.uploaded_by.username}'
    
    @property
    def is_pending(self):
        """Check if receipt is pending review."""
        return self.status == 'pending_review'
    
    @property
    def is_approved(self):
        """Check if receipt is approved."""
        return self.status == 'approved'
    
    @property
    def is_rejected(self):
        """Check if receipt is rejected."""
        return self.status == 'rejected'


class ExpenseData(models.Model):
    """Extracted/edited expense data from receipt."""
    
    CATEGORY_CHOICES = [
        ('maintenance', 'Maintenance'),
        ('utilities', 'Utilities'),
        ('cleaning', 'Cleaning'),
        ('security', 'Security'),
        ('repairs', 'Repairs'),
        ('other', 'Other'),
    ]
    
    receipt = models.OneToOneField(
        Receipt,
        on_delete=models.CASCADE,
        related_name='expense_data'
    )
    
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    vendor = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    modified_by_user = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'expense_data'
        verbose_name = 'Expense Data'
        verbose_name_plural = 'Expense Data'
    
    def __str__(self):
        return f'{self.vendor} - ${self.amount} ({self.date})'
```

- [ ] **Step 4: Update models __init__.py**

Edit `budget/models/__init__.py`:

```python
"""Budget app models."""
from .user import UserProfile
from .unit import Unit, UserUnit
from .receipt import Receipt, ExpenseData

__all__ = ['UserProfile', 'Unit', 'UserUnit', 'Receipt', 'ExpenseData']
```

- [ ] **Step 5: Create and run migrations**

```bash
python manage.py makemigrations budget
python manage.py migrate budget
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
pytest budget/tests/test_receipt_models.py -v
```

Expected: PASS

- [ ] **Step 7: Commit receipt models**

```bash
git add budget/models/ budget/tests/test_receipt_models.py budget/migrations/
git commit -m "feat: add Receipt and ExpenseData models"
```

---

## Task 2: Create Receipt Upload Form

**Files:**
- Create: `budget/forms/receipt_forms.py`
- Modify: `budget/forms/__init__.py`

- [ ] **Step 1: Implement receipt forms**

Edit `budget/forms/receipt_forms.py`:

```python
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
    
    # Admin-only field
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
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size cannot exceed 10MB.')
            
            # Check file type
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
```

- [ ] **Step 2: Update forms __init__.py**

Edit `budget/forms/__init__.py`:

```python
"""Budget app forms."""
from .auth_forms import UserRegistrationForm
from .management_forms import UnitForm, UserUnitForm
from .receipt_forms import ReceiptUploadForm, ExpenseDataForm

__all__ = [
    'UserRegistrationForm',
    'UnitForm',
    'UserUnitForm',
    'ReceiptUploadForm',
    'ExpenseDataForm'
]
```

- [ ] **Step 3: Commit receipt forms**

```bash
git add budget/forms/
git commit -m "feat: add receipt upload and expense data forms"
```

---

## Task 3: Implement Receipt Upload View with OCR

**Files:**
- Create: `budget/views/receipts.py`
- Modify: `budget/views/__init__.py`
- Create: `budget/templates/budget/receipts/upload.html`
- Create: `budget/templates/budget/receipts/list.html`

- [ ] **Step 1: Implement receipt upload view**

Edit `budget/views/receipts.py`:

```python
"""Receipt upload and management views."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from budget.decorators import any_authenticated_user
from budget.models import Receipt, ExpenseData
from budget.forms import ReceiptUploadForm, ExpenseDataForm
from budget.services import get_storage_service, get_ocr_service
from datetime import datetime


@any_authenticated_user
def receipt_upload_view(request):
    """Upload receipt with OCR processing."""
    upload_form = ReceiptUploadForm()
    expense_form = None
    receipt_url = None
    ocr_data = None
    
    if request.method == 'POST':
        if 'receipt_file' in request.FILES:
            # Step 1: Upload file
            upload_form = ReceiptUploadForm(request.POST, request.FILES)
            
            if upload_form.is_valid():
                file = upload_form.cleaned_data['receipt_file']
                
                # Determine uploader
                upload_as_user = upload_form.cleaned_data.get('upload_as_user')
                if upload_as_user and request.user.userprofile.is_admin:
                    uploader = upload_as_user
                else:
                    uploader = request.user
                
                # Upload to storage
                storage_service = get_storage_service()
                file_url = storage_service.upload_file(
                    file,
                    f'receipt_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{file.name}'
                )
                
                # Extract data with OCR
                ocr_service = get_ocr_service()
                file.seek(0)  # Reset file pointer
                ocr_data = ocr_service.extract_receipt_data(file)
                
                # Store receipt URL for display
                receipt_url = file_url
                
                # Prepare expense form with OCR data
                initial_data = {
                    'date': ocr_data.get('date') or datetime.now().date(),
                    'amount': ocr_data.get('amount') or '0.00',
                    'vendor': ocr_data.get('vendor') or '',
                    'category': ocr_data.get('category') or 'other',
                    'description': ocr_data.get('description') or '',
                }
                expense_form = ExpenseDataForm(initial=initial_data)
                
                # Store data in session for submission
                request.session['pending_receipt'] = {
                    'file_url': file_url,
                    'file_name': file.name,
                    'uploader_id': uploader.id,
                }
        
        elif 'submit_receipt' in request.POST:
            # Step 2: Submit receipt with expense data
            expense_form = ExpenseDataForm(request.POST)
            
            if expense_form.is_valid():
                pending_data = request.session.get('pending_receipt')
                
                if pending_data:
                    # Create receipt record
                    from django.contrib.auth.models import User
                    uploader = User.objects.get(id=pending_data['uploader_id'])
                    
                    receipt = Receipt.objects.create(
                        uploaded_by=uploader,
                        original_file_url=pending_data['file_url'],
                        file_name=pending_data['file_name'],
                        status='pending_review'
                    )
                    
                    # Create expense data
                    expense = expense_form.save(commit=False)
                    expense.receipt = receipt
                    expense.save()
                    
                    # Clear session
                    del request.session['pending_receipt']
                    
                    messages.success(request, 'Receipt uploaded successfully!')
                    return redirect('budget:receipt_list')
    
    # Show upload_as_user field only for admins
    if not request.user.userprofile.is_admin:
        upload_form.fields.pop('upload_as_user', None)
    
    context = {
        'upload_form': upload_form,
        'expense_form': expense_form,
        'receipt_url': receipt_url,
        'ocr_data': ocr_data,
    }
    
    return render(request, 'budget/receipts/upload.html', context)


@any_authenticated_user
def receipt_list_view(request):
    """List user's uploaded receipts."""
    if request.user.userprofile.is_admin:
        receipts = Receipt.objects.all()
    else:
        receipts = Receipt.objects.filter(uploaded_by=request.user)
    
    return render(request, 'budget/receipts/list.html', {'receipts': receipts})
```

- [ ] **Step 2: Create upload template**

Create `budget/templates/budget/receipts/upload.html`:

```html
{% extends "budget/base.html" %}

{% block title %}Upload Receipt{% endblock %}

{% block content %}
<h2>Upload Receipt</h2>

<div class="row">
    <div class="col-md-6">
        {% if not expense_form %}
        <div class="card">
            <div class="card-header">Step 1: Upload File</div>
            <div class="card-body">
                <form method="post" enctype="multipart/form-data">
                    {% csrf_token %}
                    {% for field in upload_form %}
                        <div class="mb-3">
                            <label class="form-label">{{ field.label }}</label>
                            {{ field }}
                            {% if field.errors %}
                                <div class="text-danger">{{ field.errors }}</div>
                            {% endif %}
                            {% if field.help_text %}
                                <small class="text-muted">{{ field.help_text }}</small>
                            {% endif %}
                        </div>
                    {% endfor %}
                    <button type="submit" class="btn btn-primary">Process Receipt</button>
                </form>
            </div>
        </div>
        {% else %}
        <div class="card">
            <div class="card-header">Step 2: Review & Submit</div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    {% for field in expense_form %}
                        <div class="mb-3">
                            <label class="form-label">{{ field.label }}</label>
                            {{ field }}
                            {% if field.errors %}
                                <div class="text-danger">{{ field.errors }}</div>
                            {% endif %}
                        </div>
                    {% endfor %}
                    <button type="submit" name="submit_receipt" class="btn btn-success">Submit</button>
                    <a href="{% url 'budget:receipt_upload' %}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
        {% endif %}
    </div>
    
    <div class="col-md-6">
        {% if receipt_url %}
        <div class="card">
            <div class="card-header">Receipt Preview</div>
            <div class="card-body">
                <img src="{{ receipt_url }}" alt="Receipt" class="img-fluid" />
            </div>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
```

- [ ] **Step 3: Create list template**

Create `budget/templates/budget/receipts/list.html`:

```html
{% extends "budget/base.html" %}

{% block title %}My Receipts{% endblock %}

{% block content %}
<div class="d-flex justify-content-between mb-4">
    <h2>My Receipts</h2>
    <a href="{% url 'budget:receipt_upload' %}" class="btn btn-primary">Upload Receipt</a>
</div>

<table class="table">
    <thead>
        <tr>
            <th>Date</th>
            <th>File Name</th>
            <th>Status</th>
            <th>Amount</th>
            <th>Vendor</th>
        </tr>
    </thead>
    <tbody>
        {% for receipt in receipts %}
        <tr>
            <td>{{ receipt.upload_timestamp|date:"Y-m-d" }}</td>
            <td>{{ receipt.file_name }}</td>
            <td>
                <span class="badge bg-{% if receipt.is_approved %}success{% elif receipt.is_rejected %}danger{% else %}warning{% endif %}">
                    {{ receipt.get_status_display }}
                </span>
            </td>
            <td>${{ receipt.expense_data.amount|default:'-' }}</td>
            <td>{{ receipt.expense_data.vendor|default:'-' }}</td>
        </tr>
        {% empty %}
        <tr>
            <td colspan="5" class="text-center">No receipts uploaded yet.</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

- [ ] **Step 4: Add URLs**

Add to `budget/urls.py`:

```python
from budget.views.receipts import receipt_upload_view, receipt_list_view

urlpatterns = [
    # ... existing
    path('receipts/', receipt_list_view, name='receipt_list'),
    path('receipts/upload/', receipt_upload_view, name='receipt_upload'),
]
```

- [ ] **Step 5: Update base template navigation**

Add to navbar in `budget/templates/budget/base.html`:

```html
<a class="nav-link" href="{% url 'budget:receipt_upload' %}">Upload Receipt</a>
<a class="nav-link" href="{% url 'budget:receipt_list' %}">My Receipts</a>
```

- [ ] **Step 6: Test upload flow manually**

```bash
python manage.py runserver
```

Test file upload and OCR processing

- [ ] **Step 7: Commit receipt upload feature**

```bash
git add budget/views/ budget/templates/ budget/urls.py
git commit -m "feat: implement receipt upload with OCR processing"
```

---

## Task 4: Configure Admin for Receipts

**Files:**
- Modify: `budget/admin.py`

- [ ] **Step 1: Add receipt admin**

Edit `budget/admin.py`, add:

```python
from budget.models import Receipt, ExpenseData


class ExpenseDataInline(admin.StackedInline):
    """Inline expense data for receipt."""
    model = ExpenseData
    can_delete = False


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    """Admin for receipts."""
    list_display = ['file_name', 'uploaded_by', 'status', 'upload_timestamp']
    list_filter = ['status', 'upload_timestamp']
    search_fields = ['file_name', 'uploaded_by__username']
    inlines = [ExpenseDataInline]
    readonly_fields = ['upload_timestamp', 'review_timestamp']


@admin.register(ExpenseData)
class ExpenseDataAdmin(admin.ModelAdmin):
    """Admin for expense data."""
    list_display = ['receipt', 'vendor', 'amount', 'date', 'category']
    list_filter = ['category', 'date']
    search_fields = ['vendor', 'description']
```

- [ ] **Step 2: Commit admin config**

```bash
git add budget/admin.py
git commit -m "feat: configure admin for receipts"
```

---

## Completion Checklist

- [x] Receipt and ExpenseData models created
- [x] Receipt upload form with validation
- [x] OCR integration in upload workflow
- [x] Storage service integration
- [x] User receipt list view
- [x] Admin configuration
- [x] Templates and UI complete

**Next Plan:** 2026-03-21-06-admin-review-workflow.md
