# Authentication & User Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement user authentication, role-based permissions, and user profile management with three roles: admin, tenant, and unlinked_user.

**Architecture:** Django built-in auth extended with UserProfile model, custom permissions middleware, role-based view decorators.

**Tech Stack:** Django 6.0 Auth, Django Forms, Django Permissions

---

## Task 1: Create UserProfile Model

**Files:**
- Modify: `budget/models/user.py`
- Modify: `budget/models/__init__.py`

- [ ] **Step 1: Write failing test for UserProfile model**

Edit `budget/tests/test_models.py`:

```python
"""Test suite for budget app models."""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from budget.models import UserProfile


class TestUserProfile(TestCase):
    """Test UserProfile model."""
    
    def test_create_user_profile(self):
        """Test creating a user profile with role."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        profile = UserProfile.objects.create(
            user=user,
            role='tenant',
            phone='1234567890'
        )
        
        assert profile.user == user
        assert profile.role == 'tenant'
        assert profile.phone == '1234567890'
        assert str(profile) == 'testuser (tenant)'
    
    def test_user_profile_role_choices(self):
        """Test role field accepts valid choices."""
        user = User.objects.create_user(username='admin', password='pass')
        
        # Valid roles
        for role in ['admin', 'tenant', 'unlinked_user']:
            profile = UserProfile(user=user, role=role)
            profile.full_clean()  # Should not raise validation error
    
    def test_user_profile_signal_creation(self):
        """Test profile auto-created on user creation."""
        user = User.objects.create_user(
            username='autouser',
            password='pass123'
        )
        # Profile should be auto-created with default role
        assert hasattr(user, 'userprofile')
        assert user.userprofile.role == 'tenant'  # Default role
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest budget/tests/test_models.py::TestUserProfile -v
```

Expected: FAIL - UserProfile model not defined

- [ ] **Step 3: Implement UserProfile model**

Edit `budget/models/user.py`:

```python
"""User-related models for budget app."""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with role and contact info."""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('tenant', 'Tenant'),
        ('unlinked_user', 'Unlinked User'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='userprofile'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='tenant'
    )
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"
    
    @property
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'
    
    @property
    def is_tenant(self):
        """Check if user has tenant role."""
        return self.role == 'tenant'
    
    @property
    def is_unlinked_user(self):
        """Check if user is unlinked user."""
        return self.role == 'unlinked_user'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile when User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved."""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
```

- [ ] **Step 4: Export model in __init__.py**

Edit `budget/models/__init__.py`:

```python
"""Budget app models."""
from .user import UserProfile

__all__ = ['UserProfile']
```

- [ ] **Step 5: Run test to verify it passes**

```bash
pytest budget/tests/test_models.py::TestUserProfile -v
```

Expected: FAIL - migrations not applied

- [ ] **Step 6: Create and run migrations**

```bash
python manage.py makemigrations budget
python manage.py migrate budget
```

Expected: Migration created and applied successfully

- [ ] **Step 7: Run test again to verify it passes**

```bash
pytest budget/tests/test_models.py::TestUserProfile -v
```

Expected: PASS (3 tests)

- [ ] **Step 8: Commit UserProfile model**

```bash
git add budget/models/ budget/tests/test_models.py budget/migrations/
git commit -m "feat: add UserProfile model with role-based system"
```

---

## Task 2: Create User Registration Form and View

**Files:**
- Create: `budget/forms/auth_forms.py`
- Modify: `budget/forms/__init__.py`
- Create: `budget/views/auth.py`
- Modify: `budget/views/__init__.py`
- Create: `budget/templates/budget/auth/register.html`
- Create: `budget/templates/budget/base.html`

- [ ] **Step 1: Write failing test for registration**

Edit `budget/tests/test_views.py`:

```python
"""Test suite for budget app views."""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class TestRegistrationView(TestCase):
    """Test user registration."""
    
    def setUp(self):
        self.client = Client()
    
    def test_registration_page_loads(self):
        """Test registration page is accessible."""
        response = self.client.get(reverse('budget:register'))
        assert response.status_code == 200
        assert b'Register' in response.content
    
    def test_user_registration_success(self):
        """Test successful user registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'phone': '1234567890',
        }
        response = self.client.post(reverse('budget:register'), data)
        
        # Should redirect to login
        assert response.status_code == 302
        assert User.objects.filter(username='newuser').exists()
        
        # Check profile was created
        user = User.objects.get(username='newuser')
        assert hasattr(user, 'userprofile')
        assert user.userprofile.phone == '1234567890'
    
    def test_registration_password_mismatch(self):
        """Test registration fails with password mismatch."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass123!',
        }
        response = self.client.post(reverse('budget:register'), data)
        
        assert response.status_code == 200
        assert not User.objects.filter(username='newuser').exists()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest budget/tests/test_views.py::TestRegistrationView -v
```

Expected: FAIL - views and URLs not defined

- [ ] **Step 3: Create registration form**

Edit `budget/forms/auth_forms.py`:

```python
"""Authentication forms for budget app."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from budget.models import UserProfile


class UserRegistrationForm(UserCreationForm):
    """Extended user registration form with profile fields."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        """Save user and update profile with phone."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Update the auto-created profile
            profile = user.userprofile
            profile.phone = self.cleaned_data.get('phone', '')
            profile.save()
        
        return user
```

Edit `budget/forms/__init__.py`:

```python
"""Budget app forms."""
from .auth_forms import UserRegistrationForm

__all__ = ['UserRegistrationForm']
```

- [ ] **Step 4: Create base template**

Create `budget/templates/budget/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Budget Control{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{% url 'budget:dashboard' %}">Budget Control</a>
            <div class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                    <span class="navbar-text me-3">
                        {{ user.username }} ({{ user.userprofile.role }})
                    </span>
                    <a class="nav-link" href="{% url 'budget:logout' %}">Logout</a>
                {% else %}
                    <a class="nav-link" href="{% url 'budget:login' %}">Login</a>
                    <a class="nav-link" href="{% url 'budget:register' %}">Register</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <main class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

- [ ] **Step 5: Create registration template**

Create `budget/templates/budget/auth/register.html`:

```html
{% extends "budget/base.html" %}

{% block title %}Register - Budget Control{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3>Register</h3>
            </div>
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
                                <div class="text-danger">
                                    {{ field.errors }}
                                </div>
                            {% endif %}
                            {% if field.help_text %}
                                <small class="form-text text-muted">
                                    {{ field.help_text }}
                                </small>
                            {% endif %}
                        </div>
                    {% endfor %}
                    
                    <button type="submit" class="btn btn-primary">Register</button>
                    <a href="{% url 'budget:login' %}" class="btn btn-link">
                        Already have an account? Login
                    </a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 6: Create registration view**

Edit `budget/views/auth.py`:

```python
"""Authentication views for budget app."""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from budget.forms import UserRegistrationForm


def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('budget:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'budget/auth/register.html', {'form': form})


def login_view(request):
    """User login view."""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'budget:dashboard')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    return render(request, 'budget/auth/login.html', {'form': form})


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('budget:login')
```

Edit `budget/views/__init__.py`:

```python
"""Budget app views."""
from .auth import register_view, login_view, logout_view

__all__ = ['register_view', 'login_view', 'logout_view']
```

- [ ] **Step 7: Create URL configuration**

Edit `budget/urls.py`:

```python
"""URL configuration for budget app."""
from django.urls import path
from budget.views import register_view, login_view, logout_view

app_name = 'budget'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
```

- [ ] **Step 8: Include budget URLs in project**

Edit `core/urls.py`:

```python
"""URL configuration for core project."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('budget.urls')),
]
```

- [ ] **Step 9: Create temporary dashboard URL**

Add to `budget/views/__init__.py`:

```python
from django.shortcuts import render

def dashboard_view(request):
    """Temporary dashboard placeholder."""
    return render(request, 'budget/dashboard/index.html')
```

Add to `budget/urls.py`:

```python
from budget.views import dashboard_view

urlpatterns = [
    # ... existing patterns
    path('', dashboard_view, name='dashboard'),
]
```

Create `budget/templates/budget/dashboard/index.html`:

```html
{% extends "budget/base.html" %}
{% block content %}
<h1>Dashboard (Coming Soon)</h1>
{% endblock %}
```

- [ ] **Step 10: Run tests to verify they pass**

```bash
pytest budget/tests/test_views.py::TestRegistrationView -v
```

Expected: PASS (3 tests)

- [ ] **Step 11: Commit registration feature**

```bash
git add budget/
git commit -m "feat: add user registration with profile creation"
```

---

## Task 3: Create Login Template and View

**Files:**
- Create: `budget/templates/budget/auth/login.html`

- [ ] **Step 1: Write failing test for login**

Add to `budget/tests/test_views.py`:

```python
class TestLoginView(TestCase):
    """Test user login."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_page_loads(self):
        """Test login page is accessible."""
        response = self.client.get(reverse('budget:login'))
        assert response.status_code == 200
        assert b'Login' in response.content
    
    def test_login_success(self):
        """Test successful login."""
        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = self.client.post(reverse('budget:login'), data)
        
        # Should redirect to dashboard
        assert response.status_code == 302
        assert response.url == reverse('budget:dashboard')
    
    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        data = {
            'username': 'testuser',
            'password': 'wrongpass',
        }
        response = self.client.post(reverse('budget:login'), data)
        
        # Should stay on login page
        assert response.status_code == 200
        assert b'Login' in response.content
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest budget/tests/test_views.py::TestLoginView::test_login_page_loads -v
```

Expected: FAIL - template not found

- [ ] **Step 3: Create login template**

Create `budget/templates/budget/auth/login.html`:

```html
{% extends "budget/base.html" %}

{% block title %}Login - Budget Control{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3>Login</h3>
            </div>
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
                                <div class="text-danger">
                                    {{ field.errors }}
                                </div>
                            {% endif %}
                        </div>
                    {% endfor %}
                    
                    {% if form.non_field_errors %}
                        <div class="alert alert-danger">
                            {{ form.non_field_errors }}
                        </div>
                    {% endif %}
                    
                    <button type="submit" class="btn btn-primary">Login</button>
                    <a href="{% url 'budget:register' %}" class="btn btn-link">
                        Don't have an account? Register
                    </a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest budget/tests/test_views.py::TestLoginView -v
```

Expected: PASS (3 tests)

- [ ] **Step 5: Commit login feature**

```bash
git add budget/templates/budget/auth/login.html budget/tests/test_views.py
git commit -m "feat: add login view and template"
```

---

## Task 4: Create Role-Based Permission Decorators

**Files:**
- Create: `budget/decorators.py`
- Create: `budget/tests/test_decorators.py`

- [ ] **Step 1: Write failing tests for permission decorators**

Create `budget/tests/test_decorators.py`:

```python
"""Test suite for budget app decorators."""
import pytest
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.http import HttpResponse
from budget.decorators import admin_required, tenant_or_admin_required
from budget.models import UserProfile


class TestPermissionDecorators(TestCase):
    """Test role-based permission decorators."""
    
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin', password='pass'
        )
        self.admin_user.userprofile.role = 'admin'
        self.admin_user.userprofile.save()
        
        self.tenant_user = User.objects.create_user(
            username='tenant', password='pass'
        )
        self.tenant_user.userprofile.role = 'tenant'
        self.tenant_user.userprofile.save()
        
        self.unlinked_user = User.objects.create_user(
            username='unlinked', password='pass'
        )
        self.unlinked_user.userprofile.role = 'unlinked_user'
        self.unlinked_user.userprofile.save()
    
    def test_admin_required_allows_admin(self):
        """Test admin_required allows admin users."""
        @admin_required
        def test_view(request):
            return HttpResponse('Success')
        
        request = self.factory.get('/test/')
        request.user = self.admin_user
        response = test_view(request)
        
        assert response.status_code == 200
        assert b'Success' in response.content
    
    def test_admin_required_blocks_tenant(self):
        """Test admin_required blocks tenant users."""
        @admin_required
        def test_view(request):
            return HttpResponse('Success')
        
        request = self.factory.get('/test/')
        request.user = self.tenant_user
        response = test_view(request)
        
        # Should redirect or return 403
        assert response.status_code in [302, 403]
    
    def test_tenant_or_admin_required_allows_both(self):
        """Test tenant_or_admin_required allows both roles."""
        @tenant_or_admin_required
        def test_view(request):
            return HttpResponse('Success')
        
        for user in [self.admin_user, self.tenant_user]:
            request = self.factory.get('/test/')
            request.user = user
            response = test_view(request)
            assert response.status_code == 200
    
    def test_tenant_or_admin_required_blocks_unlinked(self):
        """Test tenant_or_admin_required blocks unlinked users."""
        @tenant_or_admin_required
        def test_view(request):
            return HttpResponse('Success')
        
        request = self.factory.get('/test/')
        request.user = self.unlinked_user
        response = test_view(request)
        
        assert response.status_code in [302, 403]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest budget/tests/test_decorators.py -v
```

Expected: FAIL - decorators module not found

- [ ] **Step 3: Implement permission decorators**

Create `budget/decorators.py`:

```python
"""Custom decorators for budget app."""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def admin_required(view_func):
    """Decorator to restrict view to admin users only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'userprofile'):
            messages.error(request, 'User profile not found.')
            return redirect('budget:login')
        
        if request.user.userprofile.is_admin:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Admin access required.')
            return HttpResponseForbidden('Admin access required')
    
    return wrapper


def tenant_or_admin_required(view_func):
    """Decorator to restrict view to tenant or admin users."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'userprofile'):
            messages.error(request, 'User profile not found.')
            return redirect('budget:login')
        
        profile = request.user.userprofile
        if profile.is_admin or profile.is_tenant:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Insufficient permissions.')
            return HttpResponseForbidden('Tenant or admin access required')
    
    return wrapper


def any_authenticated_user(view_func):
    """Decorator for views accessible to any authenticated user."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return wrapper
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest budget/tests/test_decorators.py -v
```

Expected: PASS (4 tests)

- [ ] **Step 5: Commit permission decorators**

```bash
git add budget/decorators.py budget/tests/test_decorators.py
git commit -m "feat: add role-based permission decorators"
```

---

## Task 5: Configure Django Admin for User Management

**Files:**
- Modify: `budget/admin.py`

- [ ] **Step 1: Write test for admin interface**

Add to `budget/tests/test_models.py`:

```python
def test_userprofile_admin_display():
    """Test UserProfile displays correctly in admin."""
    from django.contrib import admin
    from budget.admin import UserProfileAdmin
    from budget.models import UserProfile
    
    # Check UserProfile is registered
    assert UserProfile in admin.site._registry
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest budget/tests/test_models.py::test_userprofile_admin_display -v
```

Expected: FAIL - admin not configured

- [ ] **Step 3: Configure Django admin**

Edit `budget/admin.py`:

```python
"""Django admin configuration for budget app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from budget.models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['role', 'phone', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


class UserAdmin(BaseUserAdmin):
    """Extended User admin with UserProfile inline."""
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'get_role', 'is_active', 'date_joined']
    list_filter = ['is_active', 'userprofile__role', 'date_joined']
    
    def get_role(self, obj):
        """Display user role."""
        return obj.userprofile.role if hasattr(obj, 'userprofile') else '-'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'userprofile__role'


# Unregister the default User admin
admin.site.unregister(User)

# Register the custom User admin
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile."""
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest budget/tests/test_models.py::test_userprofile_admin_display -v
```

Expected: PASS

- [ ] **Step 5: Test admin interface manually**

```bash
python manage.py runserver
```

Navigate to http://127.0.0.1:8000/admin/
Login with superuser credentials
Verify UserProfile appears in admin

- [ ] **Step 6: Commit admin configuration**

```bash
git add budget/admin.py budget/tests/test_models.py
git commit -m "feat: configure Django admin for user management"
```

---

## Task 6: Update Settings for Login Redirect

**Files:**
- Modify: `core/settings/base.py`

- [ ] **Step 1: Add authentication settings**

Edit `core/settings/base.py`, add at the end:

```python
# Authentication settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
```

- [ ] **Step 2: Test login redirect**

```bash
python manage.py runserver
```

Navigate to http://127.0.0.1:8000/
Should redirect to login page

- [ ] **Step 3: Commit settings update**

```bash
git add core/settings/base.py
git commit -m "feat: configure authentication URLs and redirects"
```

---

## Completion Checklist

After completing all tasks:

- [x] UserProfile model created with role field
- [x] User registration form and view implemented
- [x] Login/logout views created
- [x] Role-based permission decorators implemented
- [x] Django admin configured for user management
- [x] Authentication settings configured
- [x] All tests passing

**Next Plan:** 2026-03-21-03-unit-management.md
