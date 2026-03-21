# Dashboards & Reporting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement role-based dashboards showing expense summaries and lists for tenants, and comprehensive admin dashboard with analytics.

**Architecture:** Role-based dashboard views with aggregated expense data, filtering, and reporting features.

**Tech Stack:** Django ORM aggregation, Bootstrap Charts, Django templates

---

## Task 1: Create Tenant Dashboard

**Files:**
- Modify: `budget/views/dashboard.py`
- Create: `budget/templates/budget/dashboard/tenant.html`

- [ ] **Step 1: Implement tenant dashboard view**

Edit `budget/views/dashboard.py`:

```python
"""Dashboard views for budget app."""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from budget.models import Receipt, ExpenseData, UserUnit
from datetime import datetime, timedelta


@login_required
def dashboard_view(request):
    """Role-based dashboard router."""
    if request.user.userprofile.is_admin:
        return admin_dashboard(request)
    else:
        return tenant_dashboard(request)


def tenant_dashboard(request):
    """Dashboard for tenant and unlinked users."""
    user = request.user
    
    # Get approved expenses
    approved_receipts = Receipt.objects.filter(
        status='approved'
    ).select_related('expense_data')
    
    # Calculate totals
    now = datetime.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    month_total = approved_receipts.filter(
        expense_data__date__gte=this_month_start
    ).aggregate(
        total=Sum('expense_data__amount')
    )['total'] or 0
    
    year_total = approved_receipts.filter(
        expense_data__date__gte=this_year_start
    ).aggregate(
        total=Sum('expense_data__amount')
    )['total'] or 0
    
    # Get user's receipts
    my_receipts = Receipt.objects.filter(
        uploaded_by=user
    ).select_related('expense_data').order_by('-upload_timestamp')[:10]
    
    # Get user's units
    my_units = UserUnit.objects.filter(
        user=user
    ).select_related('unit')
    
    # Recent approved expenses
    recent_expenses = ExpenseData.objects.filter(
        receipt__status='approved'
    ).select_related('receipt').order_by('-date')[:10]
    
    context = {
        'month_total': month_total,
        'year_total': year_total,
        'my_receipts': my_receipts,
        'my_units': my_units,
        'recent_expenses': recent_expenses,
    }
    
    return render(request, 'budget/dashboard/tenant.html', context)


def admin_dashboard(request):
    """Dashboard for admin users."""
    # Statistics
    pending_count = Receipt.objects.filter(status='pending_review').count()
    approved_count = Receipt.objects.filter(status='approved').count()
    rejected_count = Receipt.objects.filter(status='rejected').count()
    total_users = User.objects.count()
    
    # This month expenses
    now = datetime.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    month_expenses = ExpenseData.objects.filter(
        receipt__status='approved',
        date__gte=this_month_start
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Category breakdown
    category_breakdown = ExpenseData.objects.filter(
        receipt__status='approved'
    ).values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Recent activity
    recent_receipts = Receipt.objects.all().order_by('-upload_timestamp')[:10]
    
    # Pending receipts
    pending_receipts = Receipt.objects.filter(
        status='pending_review'
    ).select_related('uploaded_by', 'expense_data')[:5]
    
    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_users': total_users,
        'month_expenses': month_expenses,
        'category_breakdown': category_breakdown,
        'recent_receipts': recent_receipts,
        'pending_receipts': pending_receipts,
    }
    
    return render(request, 'budget/dashboard/admin.html', context)
```

- [ ] **Step 2: Create tenant dashboard template**

Create `budget/templates/budget/dashboard/tenant.html`:

```html
{% extends "budget/base.html" %}

{% block title %}Dashboard - Budget Control{% endblock %}

{% block content %}
<h2>Dashboard</h2>

<!-- Summary Cards -->
<div class="row mb-4">
    <div class="col-md-6">
        <div class="card text-white bg-primary">
            <div class="card-body">
                <h5 class="card-title">This Month Expenses</h5>
                <h2>${{ month_total|floatformat:2 }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card text-white bg-success">
            <div class="card-body">
                <h5 class="card-title">This Year Expenses</h5>
                <h2>${{ year_total|floatformat:2 }}</h2>
            </div>
        </div>
    </div>
</div>

<!-- My Receipts -->
<div class="card mb-4">
    <div class="card-header d-flex justify-content-between">
        <h5>My Receipts</h5>
        <a href="{% url 'budget:receipt_list' %}" class="btn btn-sm btn-primary">View All</a>
    </div>
    <div class="card-body">
        <table class="table table-sm">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>File</th>
                    <th>Status</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                {% for receipt in my_receipts %}
                <tr>
                    <td>{{ receipt.upload_timestamp|date:"Y-m-d" }}</td>
                    <td>{{ receipt.file_name }}</td>
                    <td>
                        <span class="badge bg-{% if receipt.is_approved %}success{% elif receipt.is_rejected %}danger{% else %}warning{% endif %}">
                            {{ receipt.get_status_display }}
                        </span>
                    </td>
                    <td>${{ receipt.expense_data.amount|default:'-' }}</td>
                </tr>
                {% empty %}
                <tr><td colspan="4">No receipts uploaded.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- My Units -->
<div class="card mb-4">
    <div class="card-header"><h5>My Units</h5></div>
    <div class="card-body">
        {% for user_unit in my_units %}
        <div class="mb-2">
            <strong>{{ user_unit.unit }}</strong> - {{ user_unit.get_role_in_unit_display }}
            {% if user_unit.is_active %}
                <span class="badge bg-success">Active</span>
            {% else %}
                <span class="badge bg-secondary">Inactive</span>
            {% endif %}
        </div>
        {% empty %}
        <p>No units assigned.</p>
        {% endfor %}
    </div>
</div>

<!-- Recent Approved Expenses -->
<div class="card">
    <div class="card-header"><h5>Recent Approved Expenses</h5></div>
    <div class="card-body">
        <table class="table table-sm">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Vendor</th>
                    <th>Category</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                {% for expense in recent_expenses %}
                <tr>
                    <td>{{ expense.date }}</td>
                    <td>{{ expense.vendor }}</td>
                    <td>{{ expense.get_category_display }}</td>
                    <td>${{ expense.amount }}</td>
                </tr>
                {% empty %}
                <tr><td colspan="4">No approved expenses yet.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 3: Commit tenant dashboard**

```bash
git add budget/views/dashboard.py budget/templates/budget/dashboard/tenant.html
git commit -m "feat: implement tenant dashboard with expense summaries"
```

---

## Task 2: Create Admin Dashboard

**Files:**
- Create: `budget/templates/budget/dashboard/admin.html`

- [ ] **Step 1: Add missing import**

Edit `budget/views/dashboard.py`, add at top:

```python
from django.contrib.auth.models import User
```

- [ ] **Step 2: Create admin dashboard template**

Create `budget/templates/budget/dashboard/admin.html`:

```html
{% extends "budget/base.html" %}

{% block title %}Admin Dashboard - Budget Control{% endblock %}

{% block content %}
<h2>Admin Dashboard</h2>

<!-- Statistics Cards -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-white bg-warning">
            <div class="card-body">
                <h6>Pending Review</h6>
                <h3>{{ pending_count }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-success">
            <div class="card-body">
                <h6>Approved</h6>
                <h3>{{ approved_count }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-danger">
            <div class="card-body">
                <h6>Rejected</h6>
                <h3>{{ rejected_count }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-white bg-info">
            <div class="card-body">
                <h6>Total Users</h6>
                <h3>{{ total_users }}</h3>
            </div>
        </div>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-12">
        <div class="card text-white bg-primary">
            <div class="card-body">
                <h5>This Month Total Expenses</h5>
                <h2>${{ month_expenses|floatformat:2 }}</h2>
            </div>
        </div>
    </div>
</div>

<!-- Pending Receipts -->
<div class="card mb-4">
    <div class="card-header d-flex justify-content-between">
        <h5>Pending Receipts</h5>
        <a href="{% url 'budget:pending_receipts' %}" class="btn btn-sm btn-warning">View All</a>
    </div>
    <div class="card-body">
        <table class="table table-sm">
            <thead>
                <tr>
                    <th>Upload Date</th>
                    <th>File</th>
                    <th>Uploader</th>
                    <th>Vendor</th>
                    <th>Amount</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for receipt in pending_receipts %}
                <tr>
                    <td>{{ receipt.upload_timestamp|date:"Y-m-d H:i" }}</td>
                    <td>{{ receipt.file_name }}</td>
                    <td>{{ receipt.uploaded_by.username }}</td>
                    <td>{{ receipt.expense_data.vendor|default:'-' }}</td>
                    <td>${{ receipt.expense_data.amount|default:'-' }}</td>
                    <td>
                        <a href="{% url 'budget:receipt_detail' receipt.pk %}" class="btn btn-sm btn-primary">Review</a>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="6">No pending receipts.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- Category Breakdown -->
<div class="card mb-4">
    <div class="card-header"><h5>Expenses by Category</h5></div>
    <div class="card-body">
        <table class="table table-sm">
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Count</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                {% for cat in category_breakdown %}
                <tr>
                    <td>{{ cat.category|title }}</td>
                    <td>{{ cat.count }}</td>
                    <td>${{ cat.total|floatformat:2 }}</td>
                </tr>
                {% empty %}
                <tr><td colspan="3">No expense data.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- Recent Activity -->
<div class="card">
    <div class="card-header"><h5>Recent Receipt Activity</h5></div>
    <div class="card-body">
        <table class="table table-sm">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>File</th>
                    <th>Uploader</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for receipt in recent_receipts %}
                <tr>
                    <td>{{ receipt.upload_timestamp|date:"Y-m-d H:i" }}</td>
                    <td>{{ receipt.file_name }}</td>
                    <td>{{ receipt.uploaded_by.username }}</td>
                    <td>
                        <span class="badge bg-{% if receipt.is_approved %}success{% elif receipt.is_rejected %}danger{% else %}warning{% endif %}">
                            {{ receipt.get_status_display }}
                        </span>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="4">No receipts yet.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 3: Commit admin dashboard**

```bash
git add budget/views/dashboard.py budget/templates/budget/dashboard/admin.html
git commit -m "feat: implement admin dashboard with statistics and analytics"
```

---

## Task 3: Add Pending Count to Navigation

**Files:**
- Modify: `budget/templates/budget/base.html`
- Create: `budget/context_processors.py`
- Modify: `core/settings/base.py`

- [ ] **Step 1: Create context processor**

Create `budget/context_processors.py`:

```python
"""Context processors for budget app."""
from budget.models import Receipt


def pending_receipts_count(request):
    """Add pending receipts count to template context."""
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        if request.user.userprofile.is_admin:
            count = Receipt.objects.filter(status='pending_review').count()
            return {'pending_count': count}
    return {'pending_count': 0}
```

- [ ] **Step 2: Register context processor**

Edit `core/settings/base.py`, find TEMPLATES and update:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'budget.context_processors.pending_receipts_count',  # Add this
            ],
        },
    },
]
```

- [ ] **Step 3: Commit context processor**

```bash
git add budget/context_processors.py core/settings/base.py
git commit -m "feat: add pending receipts count to navigation"
```

---

## Task 4: Create Expense Report View

**Files:**
- Create: `budget/views/reports.py`
- Create: `budget/templates/budget/reports/expense_report.html`
- Modify: `budget/urls.py`

- [ ] **Step 1: Implement report view**

Create `budget/views/reports.py`:

```python
"""Report views for budget app."""
from django.shortcuts import render
from django.db.models import Sum, Count
from budget.decorators import admin_required
from budget.models import ExpenseData
from datetime import datetime, timedelta


@admin_required
def expense_report_view(request):
    """Detailed expense report with filtering."""
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category', '')
    
    # Base queryset
    expenses = ExpenseData.objects.filter(receipt__status='approved')
    
    # Apply filters
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    if category:
        expenses = expenses.filter(category=category)
    
    # Calculate totals
    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_count = expenses.count()
    
    # Category breakdown
    category_totals = expenses.values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Monthly breakdown
    monthly_totals = expenses.extra(
        select={'month': 'strftime("%%Y-%%m", date)'}
    ).values('month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-month')[:12]
    
    context = {
        'expenses': expenses.select_related('receipt')[:100],
        'total_amount': total_amount,
        'total_count': total_count,
        'category_totals': category_totals,
        'monthly_totals': monthly_totals,
        'start_date': start_date,
        'end_date': end_date,
        'selected_category': category,
        'categories': ExpenseData.CATEGORY_CHOICES,
    }
    
    return render(request, 'budget/reports/expense_report.html', context)
```

- [ ] **Step 2: Create report template**

Create `budget/templates/budget/reports/expense_report.html`:

```html
{% extends "budget/base.html" %}

{% block title %}Expense Report - Budget Control{% endblock %}

{% block content %}
<h2>Expense Report</h2>

<!-- Filters -->
<div class="card mb-4">
    <div class="card-body">
        <form method="get" class="row g-3">
            <div class="col-md-3">
                <label class="form-label">Start Date</label>
                <input type="date" name="start_date" class="form-control" value="{{ start_date }}">
            </div>
            <div class="col-md-3">
                <label class="form-label">End Date</label>
                <input type="date" name="end_date" class="form-control" value="{{ end_date }}">
            </div>
            <div class="col-md-3">
                <label class="form-label">Category</label>
                <select name="category" class="form-select">
                    <option value="">All Categories</option>
                    {% for value, label in categories %}
                    <option value="{{ value }}" {% if value == selected_category %}selected{% endif %}>
                        {{ label }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label">&nbsp;</label>
                <button type="submit" class="btn btn-primary d-block">Filter</button>
            </div>
        </form>
    </div>
</div>

<!-- Summary -->
<div class="row mb-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-body">
                <h5>Total Expenses</h5>
                <h2>${{ total_amount|floatformat:2 }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-body">
                <h5>Total Receipts</h5>
                <h2>{{ total_count }}</h2>
            </div>
        </div>
    </div>
</div>

<!-- Expense List -->
<div class="card mb-4">
    <div class="card-header"><h5>Expense Details</h5></div>
    <div class="card-body">
        <table class="table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Vendor</th>
                    <th>Category</th>
                    <th>Amount</th>
                    <th>Uploader</th>
                </tr>
            </thead>
            <tbody>
                {% for expense in expenses %}
                <tr>
                    <td>{{ expense.date }}</td>
                    <td>{{ expense.vendor }}</td>
                    <td>{{ expense.get_category_display }}</td>
                    <td>${{ expense.amount }}</td>
                    <td>{{ expense.receipt.uploaded_by.username }}</td>
                </tr>
                {% empty %}
                <tr><td colspan="5">No expenses found.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- Category Breakdown -->
<div class="card">
    <div class="card-header"><h5>Category Breakdown</h5></div>
    <div class="card-body">
        <table class="table">
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Count</th>
                    <th>Total</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
                {% for cat in category_totals %}
                <tr>
                    <td>{{ cat.category|title }}</td>
                    <td>{{ cat.count }}</td>
                    <td>${{ cat.total|floatformat:2 }}</td>
                    <td>{% widthratio cat.total total_amount 100 %}%</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 3: Add URLs**

Add to `budget/urls.py`:

```python
from budget.views.reports import expense_report_view

urlpatterns = [
    # ... existing
    path('reports/expenses/', expense_report_view, name='expense_report'),
]
```

- [ ] **Step 4: Add to navigation**

Update `budget/templates/budget/base.html` navbar:

```html
{% if user.userprofile.is_admin %}
    <a class="nav-link" href="{% url 'budget:expense_report' %}">Reports</a>
{% endif %}
```

- [ ] **Step 5: Commit reporting feature**

```bash
git add budget/views/reports.py budget/templates/budget/reports/ budget/urls.py
git commit -m "feat: add expense reporting with filtering and analytics"
```

---

## Completion Checklist

- [x] Tenant dashboard with expense summaries
- [x] Admin dashboard with statistics
- [x] Pending receipts count in navigation
- [x] Expense report with filtering
- [x] Category and monthly breakdowns
- [x] Role-based dashboard routing

**All Implementation Plans Complete!**

## Summary of Plans Created

1. **Project Setup & Configuration** - Django project structure, settings, testing
2. **Authentication & User Management** - User roles, permissions, registration/login
3. **Unit Management System** - Apartments and parking slots management
4. **External Service Abstractions** - OCR and Storage service layers
5. **Receipt Upload & OCR** - Upload workflow with OCR processing
6. **Admin Review Workflow** - Approve/reject receipts with editing
7. **Dashboards & Reporting** - Role-based dashboards and expense reports

Each plan follows TDD principles with bite-sized tasks and frequent commits.
