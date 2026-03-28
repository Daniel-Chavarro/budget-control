# Disable Units and Account Editing Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove Units feature completely and add account editing capability for users

**Architecture:** Two independent changes - first remove units (cleanup), then add account settings (new feature). Use TDD for account editing feature.

**Tech Stack:** Django, Python, Django Forms, Django Auth

---

## File Structure

### Units Removal
- Delete: `budget/models/unit.py`
- Modify: `budget/models/__init__.py`
- Modify: `budget/urls.py`
- Modify: `budget/views/management.py`
- Delete: `budget/templates/budget/management/unit_list.html`
- Delete: `budget/templates/budget/management/unit_form.html`
- Modify: `budget/admin.py`
- Modify: `budget/templates/budget/base.html`
- Modify: `budget/forms/__init__.py`
- Modify: `budget/forms/management_forms.py`
- Create: Django migration to drop tables

### Account Editing
- Create: `budget/forms/account_forms.py`
- Modify: `budget/forms/__init__.py`
- Create: `budget/views/account.py`
- Modify: `budget/urls.py`
- Create: `budget/templates/budget/account/account_settings.html`
- Modify: `budget/templates/budget/base.html`

---

## Chunk 1: Remove Units Feature

### Task 1: Delete unit model file and update imports

**Files:**
- Delete: `budget/models/unit.py`
- Modify: `budget/models/__init__.py:1-6`

- [ ] **Step 1: Delete unit.py model file**

Run: Delete `budget/models/unit.py`

- [ ] **Step 2: Update models/__init__.py**

```python
"""Budget app models."""
from .user import UserProfile
from .receipt import Receipt, Category

__all__ = ['UserProfile', 'Receipt', 'Category']
```

- [ ] **Step 3: Commit**

```bash
git add budget/models/unit.py budget/models/__init__.py
git commit -m "chore: remove unit model files"
```

---

### Task 2: Remove unit URLs and views

**Files:**
- Modify: `budget/urls.py:1-37`
- Modify: `budget/views/management.py:1-90` (check existing content)

- [ ] **Step 1: Check current views/management.py content**

Run: `head -60 budget/views/management.py`

- [ ] **Step 2: Remove unit URLs from urls.py**

Remove these lines from `budget/urls.py`:
```python
from budget.views.management import (
    unit_list_view, unit_create_view, unit_edit_view, unit_delete_view,
    ...
)
```
And remove:
```python
path('units/', unit_list_view, name='unit_list'),
path('units/create/', unit_create_view, name='unit_create'),
path('units/<int:pk>/edit/', unit_edit_view, name='unit_edit'),
path('units/<int:pk>/delete/', unit_delete_view, name='unit_delete'),
```

- [ ] **Step 3: Remove unit views from management.py**

Remove: `unit_list_view`, `unit_create_view`, `unit_edit_view`, `unit_delete_view` functions

- [ ] **Step 4: Commit**

```bash
git add budget/urls.py budget/views/management.py
git commit -m "chore: remove unit URLs and views"
```

---

### Task 3: Remove unit templates

**Files:**
- Delete: `budget/templates/budget/management/unit_list.html`
- Delete: `budget/templates/budget/management/unit_form.html`

- [ ] **Step 1: Delete unit templates**

Run: Delete both template files

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "chore: remove unit templates"
```

---

### Task 4: Remove unit from admin

**Files:**
- Modify: `budget/admin.py:1-68`

- [ ] **Step 1: Update admin.py**

Remove:
```python
from budget.models import Unit, UserUnit, Receipt
```
Change to:
```python
from budget.models import Receipt
```

Remove Unit and UserUnit admin registrations:
```python
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    ...

@admin.register(UserUnit)
class UserUnitAdmin(admin.ModelAdmin):
    ...
```

- [ ] **Step 2: Commit**

```bash
git add budget/admin.py
git commit -m "chore: remove unit admin registrations"
```

---

### Task 5: Remove unit navigation link

**Files:**
- Modify: `budget/templates/budget/base.html:387-392`

- [ ] **Step 1: Remove unit nav link**

Remove from base.html (lines 388-392):
```html
<li class="nav-item">
    <a class="nav-link" href="{% url 'budget:unit_list' %}">
        <i class="bi bi-building"></i>Unidades
    </a>
</li>
```

- [ ] **Step 2: Commit**

```bash
git add budget/templates/budget/base.html
git commit -m "chore: remove unit navigation link"
```

---

### Task 6: Remove unit forms

**Files:**
- Modify: `budget/forms/__init__.py:1-15`
- Modify: `budget/forms/management_forms.py` (check existing)

- [ ] **Step 1: Check management_forms.py for unit forms**

Run: `grep -n "class.*Form" budget/forms/management_forms.py`

- [ ] **Step 2: Remove unit forms from __init__.py**

Change:
```python
from .management_forms import UnitForm, UserUnitForm, UserCreateForm, CategoryForm
```
To:
```python
from .management_forms import UserCreateForm, CategoryForm
```

And update `__all__`:
```python
__all__ = [
    'UserRegistrationForm',
    'UserCreateForm',
    'CategoryForm',
    'ReceiptUploadForm',
    'TransactionForm',
    'get_category_by_name_es',
]
```

- [ ] **Step 3: Remove UnitForm and UserUnitForm from management_forms.py**

Remove `class UnitForm` and `class UserUnitForm` from `budget/forms/management_forms.py`

- [ ] **Step 4: Commit**

```bash
git add budget/forms/__init__.py budget/forms/management_forms.py
git commit -m "chore: remove unit forms"
```

---

### Task 7: Create database migration

**Files:**
- Create: New migration file in `budget/migrations/`

- [ ] **Step 1: Generate migration**

Run: `python manage.py makemigrations budget`

Expected: Django will detect removal of Unit and UserUnit models

- [ ] **Step 2: Verify migration content**

Check the generated migration file - should have:
- Delete model UserUnit
- Delete model Unit

- [ ] **Step 3: Apply migration**

Run: `python manage.py migrate`

- [ ] **Step 4: Commit**

```bash
git add budget/migrations/
git commit -m "chore: remove units and user_units tables"
```

---

## Chunk 2: Add Account Editing Feature

### Task 8: Create account forms

**Files:**
- Create: `budget/forms/account_forms.py`
- Modify: `budget/forms/__init__.py`

- [ ] **Step 1: Write failing tests for account forms**

Create test file `budget/tests/test_account_forms.py`:

```python
"""Tests for account forms."""
from django.test import TestCase
from django.contrib.auth.models import User
from budget.forms import AccountForm, PasswordChangeForm


class AccountFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='oldpassword123'
        )
        self.user.userprofile.phone = '1234567890'
        self.user.userprofile.save()

    def test_valid_form_passes(self):
        form = AccountForm(data={
            'username': 'newusername',
            'email': 'new@test.com',
            'phone': '9876543210'
        }, user=self.user)
        self.assertTrue(form.is_valid())

    def test_empty_username_fails(self):
        form = AccountForm(data={
            'username': '',
            'email': 'test@test.com',
            'phone': '1234567890'
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_duplicate_username_fails(self):
        User.objects.create_user(username='existing', email='existing@test.com')
        form = AccountForm(data={
            'username': 'existing',
            'email': 'test@test.com',
            'phone': '1234567890'
        }, user=self.user)
        self.assertFalse(form.is_valid())


class PasswordChangeFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='oldpassword123'
        )

    def test_wrong_current_password_fails(self):
        form = PasswordChangeForm(data={
            'current_password': 'wrongpassword',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('current_password', form.errors)

    def test_same_password_fails(self):
        form = PasswordChangeForm(data={
            'current_password': 'oldpassword123',
            'new_password': 'oldpassword123',
            'confirm_password': 'oldpassword123'
        }, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest budget/tests/test_account_forms.py -v`
Expected: ImportError - AccountForm and PasswordChangeForm don't exist

- [ ] **Step 3: Create account_forms.py**

```python
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
```

- [ ] **Step 4: Update forms/__init__.py**

Add to imports:
```python
from .account_forms import AccountForm, PasswordChangeForm
```

Add to __all__:
```python
'AccountForm',
'PasswordChangeForm',
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest budget/tests/test_account_forms.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add budget/forms/account_forms.py budget/forms/__init__.py budget/tests/test_account_forms.py
git commit -m "feat: add account forms with validation"
```

---

### Task 9: Create account view

**Files:**
- Create: `budget/views/account.py`
- Modify: `budget/urls.py`

- [ ] **Step 1: Write failing test for account view**

Add to `budget/tests/test_account_forms.py`:

```python
from django.test import Client
from django.urls import reverse


class AccountViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='oldpassword123'
        )
        self.client = Client()

    def test_account_page_requires_login(self):
        response = self.client.get(reverse('budget:account_settings'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_account_page_loads_for_authenticated(self):
        self.client.login(username='testuser', password='oldpassword123')
        response = self.client.get(reverse('budget:account_settings'))
        self.assertEqual(response.status_code, 200)

    def test_update_account_success(self):
        self.client.login(username='testuser', password='oldpassword123')
        response = self.client.post(reverse('budget:account_settings'), {
            'username': 'newusername',
            'email': 'new@test.com',
            'phone': '1234567890'
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newusername')
        self.assertEqual(self.user.email, 'new@test.com')
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest budget/tests/test_account_forms.py::AccountViewTest -v`
Expected: No URL pattern for account_settings

- [ ] **Step 3: Create account.py view**

```python
"""Account settings views."""
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from budget.forms import AccountForm, PasswordChangeForm


@login_required
def account_settings_view(request):
    """Display and handle account settings form."""
    if request.method == 'POST':
        # Check which form was submitted
        if 'username' in request.POST or 'email' in request.POST:
            form = AccountForm(request.POST, user=request.user)
            if form.is_valid():
                request.user.username = form.cleaned_data['username']
                request.user.email = form.cleaned_data['email']
                request.user.save()
                
                # Update phone in UserProfile
                if hasattr(request.user, 'userprofile'):
                    request.user.userprofile.phone = form.cleaned_data.get('phone', '')
                    request.user.userprofile.save()
                
                messages.success(request, 'Account details updated successfully.')
                return redirect('budget:account_settings')
        elif 'current_password' in request.POST:
            form = PasswordChangeForm(request.POST, user=request.user)
            if form.is_valid():
                request.user.set_password(form.cleaned_data['new_password'])
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully.')
                return redirect('budget:account_settings')
    else:
        initial_data = {
            'username': request.user.username,
            'email': request.user.email,
            'phone': getattr(request.user.userprofile, 'phone', '') if hasattr(request.user, 'userprofile') else '',
        }
        account_form = AccountForm(initial=initial_data, user=request.user)
        password_form = PasswordChangeForm(user=request.user)
    
    return render(request, 'budget/account/account_settings.html', {
        'account_form': account_form,
        'password_form': password_form,
    })
```

- [ ] **Step 4: Add URL for account settings**

In `budget/urls.py`, add:
```python
from budget.views.account import account_settings_view
```

Add path:
```python
path('account/', account_settings_view, name='account_settings'),
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest budget/tests/test_account_forms.py::AccountViewTest -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add budget/views/account.py budget/urls.py budget/tests/test_account_forms.py
git commit -m "feat: add account settings view"
```

---

### Task 10: Create account settings template

**Files:**
- Create: `budget/templates/budget/account/account_settings.html`
- Modify: `budget/templates/budget/base.html`

- [ ] **Step 1: Create account templates directory**

Run: `mkdir -p budget/templates/budget/account`

- [ ] **Step 2: Create account_settings.html**

```html
{% extends 'budget/base.html' %}

{% block title %}Cuenta - Control de Gastos{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="page-header">
            <h1 class="page-title">Configuración de Cuenta</h1>
            <p class="page-subtitle">Actualiza tu información personal</p>
        </div>

        <!-- Account Details Form -->
        <div class="card mb-4">
            <div class="card-header">
                <i class="bi bi-person-circle me-2"></i>Información Personal
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="id_username" class="form-label">Usuario</label>
                        <input type="text" class="form-control" id="id_username" 
                               name="username" value="{{ account_form.username.value|default:'' }}" required>
                        {% if account_form.errors.username %}
                        <div class="text-danger mt-1">
                            {% for error in account_form.errors.username %}
                            {{ error }}
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                    <div class="mb-3">
                        <label for="id_email" class="form-label">Correo Electrónico</label>
                        <input type="email" class="form-control" id="id_email" 
                               name="email" value="{{ account_form.email.value|default:'' }}" required>
                        {% if account_form.errors.email %}
                        <div class="text-danger mt-1">
                            {% for error in account_form.errors.email %}
                            {{ error }}
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                    <div class="mb-3">
                        <label for="id_phone" class="form-label">Teléfono</label>
                        <input type="text" class="form-control" id="id_phone" 
                               name="phone" value="{{ account_form.phone.value|default:'' }}">
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-check-circle me-2"></i>Guardar Cambios
                    </button>
                </form>
            </div>
        </div>

        <!-- Password Change Form -->
        <div class="card">
            <div class="card-header">
                <i class="bi bi-key me-2"></i>Cambiar Contraseña
            </div>
            <div class="card-body">
                <form method="post" action=".">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="id_current_password" class="form-label">Contraseña Actual</label>
                        <input type="password" class="form-control" id="id_current_password" 
                               name="current_password" required>
                        {% if password_form.errors.current_password %}
                        <div class="text-danger mt-1">
                            {% for error in password_form.errors.current_password %}
                            {{ error }}
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                    <div class="mb-3">
                        <label for="id_new_password" class="form-label">Nueva Contraseña</label>
                        <input type="password" class="form-control" id="id_new_password" 
                               name="new_password" required>
                        {% if password_form.errors.new_password %}
                        <div class="text-danger mt-1">
                            {% for error in password_form.errors.new_password %}
                            {{ error }}
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                    <div class="mb-3">
                        <label for="id_confirm_password" class="form-label">Confirmar Contraseña</label>
                        <input type="password" class="form-control" id="id_confirm_password" 
                               name="confirm_password" required>
                        {% if password_form.errors.confirm_password %}
                        <div class="text-danger mt-1">
                            {% for error in password_form.errors.confirm_password %}
                            {{ error }}
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                    <button type="submit" class="btn btn-warning">
                        <i class="bi bi-key me-2"></i>Cambiar Contraseña
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 3: Add Account link to navigation**

In `budget/templates/budget/base.html`, add before the Logout link:

```html
<li class="nav-item">
    <a class="nav-link" href="{% url 'budget:account_settings' %}">
        <i class="bi bi-gear"></i>Cuenta
    </a>
</li>
```

- [ ] **Step 4: Test manually**

Run dev server: `python manage.py runserver`
Navigate to `/account/` and verify:
- Form loads with current user data
- Can edit username, email, phone
- Can change password

- [ ] **Step 5: Commit**

```bash
git add budget/templates/budget/account/account_settings.html budget/templates/budget/base.html
git commit -m "feat: add account settings template and navigation"
```

---

### Task 11: Final verification

**Files:**
- All modified files

- [ ] **Step 1: Run all tests**

Run: `pytest budget/tests/ -v`

- [ ] **Step 2: Verify units removed**

Run: `python manage.py showmigrations budget`
Verify: Unit and UserUnit migrations show as applied

- [ ] **Step 3: Check for any unit references**

Run: `grep -r "Unit\|UserUnit" budget/ --include="*.py" | grep -v "__pycache__"`
Expected: No results

- [ ] **Step 4: Test account features manually**

1. Login as a user
2. Click "Cuenta" in nav
3. Edit username - save - verify
4. Edit email - save - verify
5. Change password - verify new password works

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: disable units feature and add account editing"
```

---

## Acceptance Criteria Verification

### Units Removal
- [ ] No unit-related URLs accessible (404)
- [ ] No unit links in navigation
- [ ] Unit models removed from code
- [ ] Database tables removed via migration

### Account Editing
- [ ] Account page accessible via nav link
- [ ] Username can be edited and saved
- [ ] Email can be edited and saved
- [ ] Phone can be edited and saved
- [ ] Password can be changed with current password verification
- [ ] Form validation shows appropriate errors
- [ ] Success messages displayed after save
- [ ] Users cannot edit other users' accounts
