# Spanish Data Refactor Design

## Overview
Refactor the project to use Spanish for all user-facing data including status choices, receipt types, and category names. Code variables, methods, and classes remain in English.

## Requirements
- All user-facing text in Spanish (labels, buttons, headings, messages)
- Store Spanish values directly in database choices
- Remove `name_es` field from Category model, use `name` only
- Code variables, methods, and classes stay in English

## Changes

### Models (`budget/models/receipt.py`)

**Category model:**
- Remove `name_es` field
- Change `TYPE_CHOICES` values: `expense`→`gasto`, `income`→`ingreso`
- Update `__str__` to return `self.name`

**Receipt model:**
- Change `STATUS_CHOICES`: `pending_review`→`pendiente`, `approved`→`aprobado`, `rejected`→`rechazado`
- Change `RECEIPT_TYPE_CHOICES`: `income`→`ingreso`, `expense`→`gasto`
- Update `is_pending`, `is_approved`, `is_rejected` properties to use Spanish keys
- Update default values

### Views

Update all filter/query references from English to Spanish keys:
- `budget/views/dashboard.py`
- `budget/views/receipts.py`
- `budget/views/review.py`
- `budget/views/reports.py`
- `budget/context_processors.py`

### Forms

- `budget/forms/receipt_forms.py`: Update choice keys, initial values
- Rename `get_category_by_name_es` to `get_category_by_name`

### Templates

Update all template comparisons from English to Spanish:
- `receipts/list.html`
- `receipts/upload.html`
- `review/pending_list.html`
- `review/detail.html`
- `review/all_receipts.html`
- `reports/expense_report.html`
- `management/category_list.html`
- `management/category_delete.html`
- `dashboard/tenant.html`
- `dashboard/admin.html`

### Database

Create Django migration to update existing choice values:
- `pendiente` for previously `pending_review`
- `aprobado` for previously `approved`
- `rechazado` for previously `rejected`
- `ingreso` for previously `income`
- `gasto` for previously `expense`

## Implementation Order
1. Create database migration for data values
2. Update models (remove name_es, change choices)
3. Update views and forms to use Spanish keys
4. Update templates to use Spanish keys
5. Run migrations
6. Test the application
