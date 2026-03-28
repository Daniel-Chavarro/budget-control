# Admin Review Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement admin workflow to review, approve, or reject receipts with ability to edit expense data before approval.

**Architecture:** Admin-only views with receipt detail, inline editing, approve/reject actions.

**Tech Stack:** Django views, Forms, Bootstrap UI

---

## Task 1: Create Admin Review Views

**Files:**
- Create: `budget/views/review.py`
- Modify: `budget/views/__init__.py`
- Create: `budget/templates/budget/review/pending_list.html`
- Create: `budget/templates/budget/review/detail.html`

- [ ] **Step 1: Implement review views**

Edit `budget/views/review.py`:

```python
"""Admin review workflow views."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from budget.decorators import admin_required
from budget.models import Receipt, ExpenseData
from budget.forms import ExpenseDataForm


@admin_required
def pending_receipts_view(request):
    """List all pending receipts for review."""
    pending_receipts = Receipt.objects.filter(status='pending_review')
    return render(request, 'budget/review/pending_list.html', {
        'pending_receipts': pending_receipts
    })


@admin_required
def receipt_detail_view(request, pk):
    """Detailed receipt review page."""
    receipt = get_object_or_404(Receipt, pk=pk)
    
    # Get or create expense data
    try:
        expense_data = receipt.expense_data
    except ExpenseData.DoesNotExist:
        expense_data = None
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            # Save expense data changes
            if expense_data:
                form = ExpenseDataForm(request.POST, instance=expense_data)
            else:
                form = ExpenseDataForm(request.POST)
            
            if form.is_valid():
                expense = form.save(commit=False)
                if not expense_data:
                    expense.receipt = receipt
                expense.modified_by_user = True
                expense.save()
                
                # Approve receipt
                receipt.status = 'approved'
                receipt.reviewed_by = request.user
                receipt.review_timestamp = timezone.now()
                receipt.review_notes = request.POST.get('review_notes', '')
                receipt.save()
                
                messages.success(request, f'Receipt {receipt.file_name} approved.')
                return redirect('budget:pending_receipts')
        
        elif action == 'reject':
            notes = request.POST.get('review_notes', '')
            
            if not notes:
                messages.error(request, 'Rejection notes are required.')
            else:
                receipt.status = 'rejected'
                receipt.reviewed_by = request.user
                receipt.review_timestamp = timezone.now()
                receipt.review_notes = notes
                receipt.save()
                
                messages.success(request, f'Receipt {receipt.file_name} rejected.')
                return redirect('budget:pending_receipts')
    
    # Prepare form
    if expense_data:
        expense_form = ExpenseDataForm(instance=expense_data)
    else:
        expense_form = ExpenseDataForm()
    
    context = {
        'receipt': receipt,
        'expense_form': expense_form,
    }
    
    return render(request, 'budget/review/detail.html', context)


@admin_required
def all_receipts_view(request):
    """List all receipts with filtering."""
    status_filter = request.GET.get('status', 'all')
    
    receipts = Receipt.objects.all()
    if status_filter != 'all':
        receipts = receipts.filter(status=status_filter)
    
    return render(request, 'budget/review/all_receipts.html', {
        'receipts': receipts,
        'status_filter': status_filter
    })
```

- [ ] **Step 2: Create pending receipts template**

Create `budget/templates/budget/review/pending_list.html`:

```html
{% extends "budget/base.html" %}

{% block title %}Pending Receipts - Budget Control{% endblock %}

{% block content %}
<h2>Pending Receipts for Review</h2>

<table class="table table-hover">
    <thead>
        <tr>
            <th>Upload Date</th>
            <th>File Name</th>
            <th>Uploaded By</th>
            <th>Vendor</th>
            <th>Amount</th>
            <th>Actions</th>
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
                <a href="{% url 'budget:receipt_detail' receipt.pk %}" class="btn btn-sm btn-primary">
                    Review
                </a>
            </td>
        </tr>
        {% empty %}
        <tr>
            <td colspan="6" class="text-center">No pending receipts.</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

- [ ] **Step 3: Create detail review template**

Create `budget/templates/budget/review/detail.html`:

```html
{% extends "budget/base.html" %}

{% block title %}Review Receipt - Budget Control{% endblock %}

{% block content %}
<h2>Review Receipt: {{ receipt.file_name }}</h2>

<div class="row">
    <div class="col-md-6">
        <div class="card mb-4">
            <div class="card-header">Receipt Information</div>
            <div class="card-body">
                <p><strong>Uploaded by:</strong> {{ receipt.uploaded_by.username }}</p>
                <p><strong>Upload date:</strong> {{ receipt.upload_timestamp }}</p>
                <p><strong>Status:</strong> 
                    <span class="badge bg-{{ receipt.status == 'pending_review' and 'warning' or 'secondary' }}">
                        {{ receipt.get_status_display }}
                    </span>
                </p>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">Receipt Image</div>
            <div class="card-body">
                <a href="{{ receipt.original_file_url }}" target="_blank">
                    <img src="{{ receipt.original_file_url }}" alt="Receipt" class="img-fluid" />
                </a>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">Expense Data</div>
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
                    
                    <div class="mb-3">
                        <label class="form-label">Review Notes</label>
                        <textarea name="review_notes" class="form-control" rows="3"></textarea>
                        <small class="text-muted">Required for rejection</small>
                    </div>
                    
                    <div class="d-flex gap-2">
                        <button type="submit" name="action" value="approve" class="btn btn-success">
                            Approve
                        </button>
                        <button type="submit" name="action" value="reject" class="btn btn-danger">
                            Reject
                        </button>
                        <a href="{% url 'budget:pending_receipts' %}" class="btn btn-secondary">
                            Back
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 4: Create all receipts template**

Create `budget/templates/budget/review/all_receipts.html`:

```html
{% extends "budget/base.html" %}

{% block content %}
<h2>All Receipts</h2>

<div class="mb-3">
    <a href="?status=all" class="btn btn-sm btn-outline-primary">All</a>
    <a href="?status=pending_review" class="btn btn-sm btn-outline-warning">Pending</a>
    <a href="?status=approved" class="btn btn-sm btn-outline-success">Approved</a>
    <a href="?status=rejected" class="btn btn-sm btn-outline-danger">Rejected</a>
</div>

<table class="table">
    <thead>
        <tr>
            <th>Date</th>
            <th>File</th>
            <th>Uploader</th>
            <th>Status</th>
            <th>Vendor</th>
            <th>Amount</th>
        </tr>
    </thead>
    <tbody>
        {% for receipt in receipts %}
        <tr>
            <td>{{ receipt.upload_timestamp|date:"Y-m-d" }}</td>
            <td>{{ receipt.file_name }}</td>
            <td>{{ receipt.uploaded_by.username }}</td>
            <td><span class="badge bg-{{ receipt.is_approved and 'success' or 'warning' }}">{{ receipt.get_status_display }}</span></td>
            <td>{{ receipt.expense_data.vendor|default:'-' }}</td>
            <td>${{ receipt.expense_data.amount|default:'-' }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

- [ ] **Step 5: Add URLs**

Add to `budget/urls.py`:

```python
from budget.views.review import (
    pending_receipts_view, receipt_detail_view, all_receipts_view
)

urlpatterns = [
    # ... existing
    path('review/pending/', pending_receipts_view, name='pending_receipts'),
    path('review/<int:pk>/', receipt_detail_view, name='receipt_detail'),
    path('review/all/', all_receipts_view, name='all_receipts'),
]
```

- [ ] **Step 6: Update navigation**

Add to `budget/templates/budget/base.html` navbar:

```html
{% if user.userprofile.is_admin %}
    <a class="nav-link" href="{% url 'budget:pending_receipts' %}">
        Pending Reviews
        {% if pending_count %}<span class="badge bg-danger">{{ pending_count }}</span>{% endif %}
    </a>
{% endif %}
```

- [ ] **Step 7: Commit review workflow**

```bash
git add budget/views/ budget/templates/ budget/urls.py
git commit -m "feat: implement admin receipt review workflow"
```

---

## Completion Checklist

- [x] Pending receipts list view
- [x] Receipt detail review page
- [x] Approve/reject functionality
- [x] Expense data inline editing
- [x] Review notes support
- [x] All receipts view with filtering

**Next Plan:** 2026-03-21-07-dashboards-reporting.md
