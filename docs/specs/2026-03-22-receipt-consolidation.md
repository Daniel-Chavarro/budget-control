# Refactor: Consolidate ExpenseData and IncomeData into Receipt

**Date:** 2026-03-22  
**Status:** Draft

## Goal

Merge `ExpenseData` and `IncomeData` tables into the `Receipt` table to simplify data structure and reduce code complexity.

## Current State

### Tables
- **receipts**: File metadata, receipt_type (income/expense), status
- **expense_data**: OneToOne to receipt - vendor, amount, date, category
- **income_data**: OneToOne to receipt - payer, amount, date, category

### Issues
- Data spread across 3 tables
- Queries need to check `receipt.expense_data` or `receipt.income_data`
- Duplicate fields (amount, date, category, description, modified_by_user)
- Extra join queries for reports/dashboards

## Proposed Design

### New Receipt Table Structure

| Field | Type | Description |
|-------|------|-------------|
| id | BigAuto | Primary key |
| uploaded_by | FK(User) | Uploader |
| original_file_url | URL | File storage URL |
| file_name | Char(255) | Original filename |
| upload_timestamp | DateTime | When uploaded |
| receipt_type | Char(10) | income or expense |
| status | Char(20) | pending_review/approved/rejected |
| reviewed_by | FK(User) | Admin who reviewed |
| review_timestamp | DateTime | When reviewed |
| review_notes | Text | Review comments |
| **date** | Date | Transaction date (NEW) |
| **amount** | Decimal(10,2) | Transaction amount (NEW) |
| **category** | FK(Category) | Category (filtered by receipt_type) (NEW) |
| **counterparty** | Char(200) | vendor (expense) or payer (income) (NEW) |
| **description** | Text | Notes (NEW) |
| **modified_by_user** | Boolean | If user edited OCR data (NEW) |

### Key Changes

1. **Unified `counterparty` field**: 
   - For expenses: "vendor" 
   - For income: "payer"
   
2. **Category filtering**:
   - Use Django's `limit_choices_to` to restrict category based on `receipt_type`
   - Can be implemented in forms, not at DB level

3. **Data migration**:
   - Copy expense_data fields to receipts WHERE receipt_type = 'expense'
   - Copy income_data fields to receipts WHERE receipt_type = 'income'
   - Map: vendor → counterparty, payer → counterparty

4. **Deprecated models**:
   - Keep ExpenseData and IncomeData temporarily
   - Delete after migration verified

## Implementation Steps

1. Add new fields to Receipt model (without deleting old models)
2. Create and run Django migration
3. Create data migration script to copy values
4. Update forms (ReceiptUploadForm, ExpenseDataForm, IncomeDataForm)
5. Update views (receipts.py, dashboard.py, reports.py, review.py)
6. Update templates
7. Run tests and verify
8. Delete old ExpenseData and IncomeData models
9. Final migration cleanup

## Affected Files

- budget/models/receipt.py
- budget/forms/receipt_forms.py
- budget/views/receipts.py
- budget/views/dashboard.py
- budget/views/reports.py
- budget/views/review.py
- budget/templates/budget/receipts/*.html
- budget/templates/budget/dashboard/*.html
- budget/templates/budget/reports/*.html
- budget/templates/budget/review/*.html

## Backward Compatibility

- Old data will be migrated to new structure
- No URL changes required
- Same API for forms/views after update