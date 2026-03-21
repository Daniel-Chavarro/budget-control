# Unit Management System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement unit management (apartments and parking slots) with user-unit relationships tracking ownership and rental periods.

**Architecture:** Django ORM models for Unit and UserUnit with many-to-many relationships, admin-only CRUD views.

**Tech Stack:** Django 6.0 Forms, Django ORM, Bootstrap UI

---

## Task 1: Create Unit and UserUnit Models

**Files:**
- Create: `budget/models/unit.py`
- Modify: `budget/models/__init__.py`
- Create: `budget/tests/test_unit_models.py`

- [ ] **Step 1: Write failing tests**

Create `budget/tests/test_unit_models.py`:

```python
"""Test suite for unit models."""
from django.test import TestCase
from django.contrib.auth.models import User
from budget.models import Unit, UserUnit
from decimal import Decimal
from datetime import date, timedelta


class TestUnitModel(TestCase):
    """Test Unit model."""
    
    def test_create_apartment_unit(self):
        """Test creating apartment unit."""
        unit = Unit.objects.create(
            type='apartment',
            identifier='A-101',
            status='active',
            monthly_fee=Decimal('150.00')
        )
        assert unit.identifier == 'A-101'
        assert unit.type == 'apartment'
        assert unit.is_apartment
        assert not unit.is_parking
        assert str(unit) == 'Apartment A-101'
    
    def test_create_parking_unit(self):
        """Test creating parking unit."""
        unit = Unit.objects.create(
            type='public_parking',
            identifier='P-05',
            status='active',
            monthly_fee=Decimal('50.00')
        )
        assert unit.is_parking
        assert str(unit) == 'Parking P-05'


class TestUserUnitModel(TestCase):
    """Test UserUnit relationship model."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='tenant', password='pass')
        self.unit = Unit.objects.create(
            type='apartment',
            identifier='A-201',
            status='active'
        )
    
    def test_create_user_unit_relationship(self):
        """Test creating user-unit relationship."""
        user_unit = UserUnit.objects.create(
            user=self.user,
            unit=self.unit,
            role_in_unit='owner',
            start_date=date.today()
        )
        assert user_unit.user == self.user
        assert user_unit.unit == self.unit
        assert user_unit.is_active
        assert str(user_unit) == f'tenant - Apartment A-201 (owner)'
    
    def test_user_unit_active_status(self):
        """Test is_active property."""
        # Active: no end_date
        active = UserUnit.objects.create(
            user=self.user,
            unit=self.unit,
            role_in_unit='tenant',
            start_date=date.today()
        )
        assert active.is_active
        
        # Inactive: end_date in past
        inactive = UserUnit.objects.create(
            user=self.user,
            unit=self.unit,
            role_in_unit='tenant',
            start_date=date.today() - timedelta(days=60),
            end_date=date.today() - timedelta(days=1)
        )
        assert not inactive.is_active
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest budget/tests/test_unit_models.py -v
```

Expected: FAIL - models not defined

- [ ] **Step 3: Implement Unit model**

Create `budget/models/unit.py`:

```python
"""Unit-related models for budget app."""
from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Unit(models.Model):
    """Apartment or parking slot unit."""
    
    TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('public_parking', 'Public Parking'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    identifier = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Monthly fee if applicable'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'units'
        verbose_name = 'Unit'
        verbose_name_plural = 'Units'
        ordering = ['identifier']
    
    def __str__(self):
        type_label = 'Apartment' if self.type == 'apartment' else 'Parking'
        return f'{type_label} {self.identifier}'
    
    @property
    def is_apartment(self):
        """Check if unit is apartment."""
        return self.type == 'apartment'
    
    @property
    def is_parking(self):
        """Check if unit is parking."""
        return self.type == 'public_parking'


class UserUnit(models.Model):
    """Many-to-many relationship between users and units."""
    
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('tenant', 'Tenant'),
        ('authorized_user', 'Authorized User'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_units')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='unit_users')
    role_in_unit = models.CharField(max_length=20, choices=ROLE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_units'
        verbose_name = 'User Unit Relationship'
        verbose_name_plural = 'User Unit Relationships'
        unique_together = [['user', 'unit', 'start_date']]
    
    def __str__(self):
        return f'{self.user.username} - {self.unit} ({self.role_in_unit})'
    
    @property
    def is_active(self):
        """Check if relationship is currently active."""
        if self.end_date is None:
            return True
        return self.end_date >= date.today()
```

- [ ] **Step 4: Update models __init__.py**

Edit `budget/models/__init__.py`:

```python
"""Budget app models."""
from .user import UserProfile
from .unit import Unit, UserUnit

__all__ = ['UserProfile', 'Unit', 'UserUnit']
```

- [ ] **Step 5: Create and run migrations**

```bash
python manage.py makemigrations budget
python manage.py migrate budget
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
pytest budget/tests/test_unit_models.py -v
```

Expected: PASS (all tests)

- [ ] **Step 7: Commit unit models**

```bash
git add budget/models/ budget/tests/test_unit_models.py budget/migrations/
git commit -m "feat: add Unit and UserUnit models"
```

---

## Task 2: Create Unit Management Forms

**Files:**
- Create: `budget/forms/management_forms.py`
- Modify: `budget/forms/__init__.py`

- [ ] **Step 1: Create unit management forms**

Edit `budget/forms/management_forms.py`:

```python
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
```

- [ ] **Step 2: Update forms __init__.py**

Edit `budget/forms/__init__.py`:

```python
"""Budget app forms."""
from .auth_forms import UserRegistrationForm
from .management_forms import UnitForm, UserUnitForm

__all__ = ['UserRegistrationForm', 'UnitForm', 'UserUnitForm']
```

- [ ] **Step 3: Commit forms**

```bash
git add budget/forms/
git commit -m "feat: add unit management forms"
```

---

## Task 3: Create Unit Management Views (Admin Only)

**Files:**
- Modify: `budget/views/management.py`
- Create: `budget/templates/budget/management/unit_list.html`
- Create: `budget/templates/budget/management/unit_form.html`
- Modify: `budget/urls.py`

- [ ] **Step 1: Implement unit management views**

Edit `budget/views/management.py`:

```python
"""Management views for units and users (admin only)."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from budget.decorators import admin_required
from budget.models import Unit, UserUnit
from budget.forms import UnitForm, UserUnitForm


@admin_required
def unit_list_view(request):
    """List all units."""
    units = Unit.objects.all()
    return render(request, 'budget/management/unit_list.html', {'units': units})


@admin_required
def unit_create_view(request):
    """Create new unit."""
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f'Unit {unit.identifier} created successfully.')
            return redirect('budget:unit_list')
    else:
        form = UnitForm()
    
    return render(request, 'budget/management/unit_form.html', {
        'form': form,
        'action': 'Create'
    })


@admin_required
def unit_edit_view(request, pk):
    """Edit existing unit."""
    unit = get_object_or_404(Unit, pk=pk)
    
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f'Unit {unit.identifier} updated successfully.')
            return redirect('budget:unit_list')
    else:
        form = UnitForm(instance=unit)
    
    return render(request, 'budget/management/unit_form.html', {
        'form': form,
        'action': 'Edit',
        'unit': unit
    })


@admin_required
def unit_delete_view(request, pk):
    """Delete unit."""
    unit = get_object_or_404(Unit, pk=pk)
    identifier = unit.identifier
    unit.delete()
    messages.success(request, f'Unit {identifier} deleted successfully.')
    return redirect('budget:unit_list')
```

- [ ] **Step 2: Create unit list template**

Create `budget/templates/budget/management/unit_list.html`:

```html
{% extends "budget/base.html" %}

{% block title %}Units - Budget Control{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h2>Units</h2>
    <a href="{% url 'budget:unit_create' %}" class="btn btn-primary">Add Unit</a>
</div>

<table class="table table-striped">
    <thead>
        <tr>
            <th>Type</th>
            <th>Identifier</th>
            <th>Status</th>
            <th>Monthly Fee</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for unit in units %}
        <tr>
            <td>{{ unit.get_type_display }}</td>
            <td>{{ unit.identifier }}</td>
            <td>
                <span class="badge bg-{{ unit.status == 'active' and 'success' or 'secondary' }}">
                    {{ unit.get_status_display }}
                </span>
            </td>
            <td>${{ unit.monthly_fee|default:'-' }}</td>
            <td>
                <a href="{% url 'budget:unit_edit' unit.pk %}" class="btn btn-sm btn-outline-primary">Edit</a>
                <form method="post" action="{% url 'budget:unit_delete' unit.pk %}" style="display:inline;">
                    {% csrf_token %}
                    <button type="submit" class="btn btn-sm btn-outline-danger" 
                            onclick="return confirm('Delete this unit?')">Delete</button>
                </form>
            </td>
        </tr>
        {% empty %}
        <tr>
            <td colspan="5" class="text-center">No units found.</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

- [ ] **Step 3: Create unit form template**

Create `budget/templates/budget/management/unit_form.html`:

```html
{% extends "budget/base.html" %}

{% block title %}{{ action }} Unit - Budget Control{% endblock %}

{% block content %}
<h2>{{ action }} Unit</h2>

<div class="card">
    <div class="card-body">
        <form method="post">
            {% csrf_token %}
            
            {% for field in form %}
                <div class="mb-3">
                    <label for="{{ field.id_for_label }}" class="form-label">
                        {{ field.label }}
                    </label>
                    {{ field }}
                    {% if field.errors %}
                        <div class="text-danger">{{ field.errors }}</div>
                    {% endif %}
                    {% if field.help_text %}
                        <small class="form-text text-muted">{{ field.help_text }}</small>
                    {% endif %}
                </div>
            {% endfor %}
            
            <button type="submit" class="btn btn-primary">Save</button>
            <a href="{% url 'budget:unit_list' %}" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 4: Add URLs**

Add to `budget/urls.py`:

```python
from budget.views.management import (
    unit_list_view, unit_create_view, unit_edit_view, unit_delete_view
)

urlpatterns = [
    # ... existing patterns
    path('units/', unit_list_view, name='unit_list'),
    path('units/create/', unit_create_view, name='unit_create'),
    path('units/<int:pk>/edit/', unit_edit_view, name='unit_edit'),
    path('units/<int:pk>/delete/', unit_delete_view, name='unit_delete'),
]
```

- [ ] **Step 5: Update base template navigation**

Edit `budget/templates/budget/base.html`, add to navbar:

```html
{% if user.is_authenticated and user.userprofile.is_admin %}
    <a class="nav-link" href="{% url 'budget:unit_list' %}">Units</a>
{% endif %}
```

- [ ] **Step 6: Test manually**

```bash
python manage.py runserver
```

Login as admin, navigate to /units/, test CRUD operations

- [ ] **Step 7: Commit unit management views**

```bash
git add budget/views/management.py budget/templates/budget/management/ budget/urls.py
git commit -m "feat: add unit management views (admin only)"
```

---

## Task 4: Configure Django Admin for Units

**Files:**
- Modify: `budget/admin.py`

- [ ] **Step 1: Add unit admin configuration**

Edit `budget/admin.py`, add:

```python
from budget.models import Unit, UserUnit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """Admin interface for Unit."""
    list_display = ['identifier', 'type', 'status', 'monthly_fee', 'created_at']
    list_filter = ['type', 'status', 'created_at']
    search_fields = ['identifier']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserUnit)
class UserUnitAdmin(admin.ModelAdmin):
    """Admin interface for UserUnit."""
    list_display = ['user', 'unit', 'role_in_unit', 'start_date', 'end_date', 'is_active']
    list_filter = ['role_in_unit', 'start_date']
    search_fields = ['user__username', 'unit__identifier']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
```

- [ ] **Step 2: Test admin interface**

```bash
python manage.py runserver
```

Navigate to /admin/, verify Unit and UserUnit appear

- [ ] **Step 3: Commit admin updates**

```bash
git add budget/admin.py
git commit -m "feat: configure Django admin for unit management"
```

---

## Completion Checklist

- [x] Unit and UserUnit models created
- [x] Unit management forms implemented
- [x] Admin-only CRUD views for units
- [x] Django admin configured for units
- [x] All tests passing

**Next Plan:** 2026-03-21-04-external-services.md
