# Spanish Data Refactor Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert all user-facing data to Spanish while keeping code variables in English

**Architecture:** Update database choice values, models, views, forms, and templates to use Spanish keys for all user-facing data

**Tech Stack:** Django, Python, HTML templates

---

## File Structure

- Modify: `budget/models/receipt.py` - Update choices and remove name_es
- Modify: `budget/views/dashboard.py` - Update filter keys
- Modify: `budget/views/receipts.py` - Update status/receipt_type references
- Modify: `budget/views/receipts.py` - Update upload logic keys
- Modify: `budget/views/review.py` - Update status change keys
- Modify: `budget/views/reports.py` - Update filter keys
- Modify: `budget/context_processors.py` - Update filter keys
- Modify: `budget/forms/receipt_forms.py` - Update choices and rename helper
- Modify: Multiple templates (10 files) - Update template comparisons
- Create: Migration file for data update

---

## Chunk 1: Database Migration

- [ ] **Step 1: Create Django migration for data update**

Run:
```bash
cd C:/Users/CH3/Documents/GitHub/budget-control
python manage.py makemigrations budget --name spanish_data_migration
```

- [ ] **Step 2: Edit the migration to update existing data values**

Modify generated migration file to add data migrations:

```python
from django.db import migrations

def update_spanish_choices(apps, schema_editor):
    Receipt = apps.get_model('budget', 'Receipt')
    Category = apps.get_model('budget', 'Category')
    
    # Update Receipt status
    Receipt.objects.filter(status='pending_review').update(status='pendiente')
    Receipt.objects.filter(status='approved').update(status='aprobado')
    Receipt.objects.filter(status='rejected').update(status='rechazado')
    
    # Update Receipt receipt_type
    Receipt.objects.filter(receipt_type='income').update(receipt_type='ingreso')
    Receipt.objects.filter(receipt_type='expense').update(receipt_type='gasto')
    
    # Update Category category_type
    Category.objects.filter(category_type='income').update(category_type='ingreso')
    Category.objects.filter(category_type='expense').update(category_type='gasto')

def reverse_choices(apps, schema_editor):
    Receipt = apps.get_model('budget', 'Receipt')
    Category = apps.get_model('budget', 'Category')
    
    Receipt.objects.filter(status='pendiente').update(status='pending_review')
    Receipt.objects.filter(status='aprobado').update(status='approved')
    Receipt.objects.filter(status='rechazado').update(status='rejected')
    
    Receipt.objects.filter(receipt_type='ingreso').update(receipt_type='income')
    Receipt.objects.filter(receipt_type='gasto').update(receipt_type='expense')
    
    Category.objects.filter(category_type='ingreso').update(category_type='income')
    Category.objects.filter(category_type='gasto').update(category_type='expense')

class Migration(migrations.Migration):
    dependencies = [
        ('budget', 'previous_migration_name'),
    ]
    
    operations = [
        migrations.RunPython(update_spanish_choices, reverse_choices),
    ]
```

- [ ] **Step 3: Commit**

```bash
git add budget/migrations/
git commit -m "feat: add data migration for Spanish choice values"
```

---

## Chunk 2: Models

- [ ] **Step 1: Modify budget/models/receipt.py**

Replace STATUS_CHOICES:
```python
STATUS_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('aprobado', 'Aprobado'),
    ('rechazado', 'Rechazado'),
]
```

Replace RECEIPT_TYPE_CHOICES:
```python
RECEIPT_TYPE_CHOICES = [
    ('ingreso', 'Ingreso'),
    ('gasto', 'Gasto'),
]
```

Replace TYPE_CHOICES in Category:
```python
TYPE_CHOICES = [
    ('gasto', 'Gasto'),
    ('ingreso', 'Ingreso'),
]
```

Remove name_es field and update __str__:
```python
# Remove this line:
name_es = models.CharField('Nombre en espanol', max_length=50)

# Update __str__ to:
def __str__(self):
    return f'{self.name}'
```

Update default values:
```python
receipt_type = models.CharField(
    max_length=10,
    choices=RECEIPT_TYPE_CHOICES,
    default='gasto'
)

status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default='pendiente'
)
```

Update properties:
```python
@property
def is_pending(self):
    return self.status == 'pendiente'

@property
def is_approved(self):
    return self.status == 'aprobado'

@property
def is_rejected(self):
    return self.status == 'rechazado'
```

- [ ] **Step 2: Create model migration**

Run:
```bash
python manage.py makemigrations budget --name spanish_choices_model
```

- [ ] **Step 3: Commit**

```bash
git add budget/models/receipt.py budget/migrations/
git commit -m "refactor: update choices to Spanish in models"
```

---

## Chunk 3: Views

- [ ] **Step 1: Modify budget/views/dashboard.py**

Update all filter keys:
```python
# Line 28-29: change 'approved' to 'aprobado', 'income' to 'ingreso'
# Line 35-36: change 'approved' to 'aprobado', 'income' to 'ingreso'
# Line 46-47: change 'approved' to 'aprobado', 'income' to 'ingreso'
# Line 63: change 'pending_review' to 'pendiente'
# Line 64: change 'approved' to 'aprobado'
# Line 65: change 'rejected' to 'rechazado'
# Line 72-73: change 'approved' to 'aprobado', 'expense' to 'gasto'
# Line 78-79: change 'approved' to 'aprobado', 'income' to 'ingreso'
# Line 84-85: change 'approved' to 'aprobado', 'expense' to 'gasto'
# Line 92-93: change 'approved' to 'aprobado', 'income' to 'ingreso'
# Line 102: change 'pending_review' to 'pendiente'
```

- [ ] **Step 2: Modify budget/views/receipts.py**

Update lines with status/receipt_type:
- Lines 68, 70, 143, 145, 165, 197, 245, 247, 250

- [ ] **Step 3: Modify budget/views/review.py**

- Line 16: 'pending_review' → 'pendiente'
- Line 45: 'approved' → 'aprobado'
- Line 63: 'rejected' → 'rechazado'

- [ ] **Step 4: Modify budget/views/reports.py**

- Line 32-33: 'expense' → 'gasto', 'income' → 'ingreso'
- Line 35: 'approved' → 'aprobado'
- Line 47-48: 'expense' → 'gasto', 'income' → 'ingreso'
- Lines 65-66: filter keys

- [ ] **Step 5: Modify budget/context_processors.py**

- Line 9: 'pending_review' → 'pendiente'

- [ ] **Step 6: Commit**

```bash
git add budget/views/dashboard.py budget/views/receipts.py budget/views/review.py budget/views/reports.py budget/context_processors.py
git commit -m "refactor: update view filters to Spanish keys"
```

---

## Chunk 4: Forms

- [ ] **Step 1: Modify budget/forms/receipt_forms.py**

Update RECEIPT_TYPE_CHOICES:
```python
choices=Receipt.RECEIPT_TYPE_CHOICES,  # Already uses model choices
```

Update initial value:
```python
initial='gasto'  # Line 23
```

Update clean method:
```python
return self.cleaned_data.get('receipt_type') or 'ingreso'  # Line 36
```

Rename helper function:
```python
def get_category_by_name(name: str, category_type: str = 'gasto'):  # Line 53
```

Update TransactionForm:
```python
def __init__(self, *args, receipt_type='gasto', **kwargs):  # Line 66
if receipt_type == 'gasto':  # Line 75
```

- [ ] **Step 2: Commit**

```bash
git add budget/forms/receipt_forms.py
git commit -m "refactor: update forms to Spanish keys"
```

---

## Chunk 5: Templates

- [ ] **Step 1: Modify budget/templates/budget/receipts/list.html**

- Line 39: `'income'` → `'ingreso'`
- Line 46: `'approved'` → `'aprobado'`
- Line 48: `'rejected'` → `'rechazado'`
- Line 55: `'income'` → `'ingreso'`

- [ ] **Step 2: Modify budget/templates/budget/receipts/upload.html**

- Line 120: `'income'` → `'ingreso'`

- [ ] **Step 3: Modify budget/templates/budget/review/pending_list.html**

- Line 35: `'income'` → `'ingreso'`

- [ ] **Step 4: Modify budget/templates/budget/review/detail.html**

- Line 36: `'pending_review'` → `'pendiente'`
- Line 38: `'approved'` → `'aprobado'`
- Line 63: `'income'` → `'ingreso'`

- [ ] **Step 5: Modify budget/templates/budget/review/all_receipts.html**

- Lines 17, 20, 23: update status filter links
- Line 57: `'approved'` → `'aprobado'`
- Line 59: `'rejected'` → `'rechazado'`

- [ ] **Step 6: Modify budget/templates/budget/reports/expense_report.html**

- Lines 26-27: option values `'expense'` → `'gasto'`, `'income'` → `'ingreso'`
- Lines 34-35, 41-42: update type comparisons

- [ ] **Step 7: Modify budget/templates/budget/management/category_list.html**

- Line 31: `'expense'` → `'gasto'`
- Line 78: `'income'` → `'ingreso'`

- [ ] **Step 8: Modify budget/templates/budget/management/category_delete.html**

- Line 23: `'expense'` → `'gasto'`

- [ ] **Step 9: Modify budget/templates/budget/dashboard/tenant.html**

- Line 73: `'approved'` → `'aprobado'`
- Line 75: `'rejected'` → `'rechazado'`

- [ ] **Step 10: Modify budget/templates/budget/dashboard/admin.html**

- Lines 138, 149, 246: `'income'` → `'ingreso'`
- Lines 257, 259: `'approved'` → `'aprobado'`, `'rejected'` → `'rechazado'`

- [ ] **Step 11: Commit**

```bash
git add budget/templates/
git commit -m "refactor: update templates to Spanish keys"
```

---

## Chunk 6: Test and Verify

- [ ] **Step 1: Run migrations**

```bash
python manage.py migrate
```

- [ ] **Step 2: Run tests**

```bash
pytest -v
```

- [ ] **Step 3: Start server and verify**

```bash
python manage.py runserver
```

- [ ] **Step 4: Final commit**

```bash
git add .
git commit -m "feat: complete Spanish data refactor"
```
