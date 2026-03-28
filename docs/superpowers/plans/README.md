# Budget Control Implementation Plans - Index

**Created:** 2026-03-21  
**Based on Spec:** docs/superpowers/specs/2026-03-14-budget-control-design.md

## Overview

This directory contains 7 comprehensive implementation plans for the Budget Control System, a Django-based apartment administration budget tracking application with receipt OCR processing and admin approval workflows.

## Plan Execution Order

The plans should be executed in the following order, as each builds upon the previous:

### 1. Project Setup & Configuration
**File:** `2026-03-21-01-project-setup.md`  
**Duration:** ~2-3 hours  
**Description:** Sets up Django project structure, splits settings into environments, configures testing framework, and creates the budget app with directory structure.

**Key Deliverables:**
- Settings split (base/development/production)
- Dependencies installed and organized
- Budget app created with proper structure
- Testing framework configured (pytest + coverage)
- Environment variables template

---

### 2. Authentication & User Management
**File:** `2026-03-21-02-authentication-user-management.md`  
**Duration:** ~3-4 hours  
**Description:** Implements user authentication system with three roles (admin, tenant, unlinked_user), registration, login, and role-based permission decorators.

**Key Deliverables:**
- UserProfile model with role field
- User registration and login views
- Role-based permission decorators
- Django admin configuration for users
- Authentication templates

---

### 3. Unit Management System
**File:** `2026-03-21-03-unit-management.md`  
**Duration:** ~2-3 hours  
**Description:** Implements management of apartments and parking slots with user-unit relationships tracking ownership and rental periods.

**Key Deliverables:**
- Unit and UserUnit models
- Admin-only CRUD views for units
- Unit management forms
- Django admin configuration
- Unit assignment tracking

---

### 4. External Service Abstractions
**File:** `2026-03-21-04-external-services.md`  
**Duration:** ~3-4 hours  
**Description:** Creates abstraction layers for OCR (Gemini/OpenRouter) and Storage (Google Drive/Cloudinary) services with swappable providers.

**Key Deliverables:**
- Storage service abstraction (Google Drive, Cloudinary)
- OCR service abstraction (Gemini, OpenRouter)
- Factory pattern for provider selection
- Service integration tests
- Configuration via environment variables

---

### 5. Receipt Upload & OCR Processing
**File:** `2026-03-21-05-receipt-upload-ocr.md`  
**Duration:** ~4-5 hours  
**Description:** Implements the core receipt upload workflow with OCR extraction, allowing tenants to upload receipts and admins to upload on behalf of users.

**Key Deliverables:**
- Receipt and ExpenseData models
- Upload form with file validation
- OCR integration in workflow
- Storage service integration
- Two-step upload process (file → data review)
- Receipt list view

---

### 6. Admin Review Workflow
**File:** `2026-03-21-06-admin-review-workflow.md`  
**Duration:** ~2-3 hours  
**Description:** Implements admin workflow to review, approve, or reject receipts with ability to edit expense data before approval.

**Key Deliverables:**
- Pending receipts list view
- Receipt detail review page
- Approve/reject functionality
- Expense data inline editing
- Review notes support
- All receipts view with filtering

---

### 7. Dashboards & Reporting
**File:** `2026-03-21-07-dashboards-reporting.md`  
**Duration:** ~3-4 hours  
**Description:** Implements role-based dashboards showing expense summaries for tenants and comprehensive admin dashboard with analytics and reporting.

**Key Deliverables:**
- Tenant dashboard with expense summaries
- Admin dashboard with statistics
- Pending receipts count in navigation
- Expense report with filtering
- Category and monthly breakdowns
- Role-based dashboard routing

---

## Total Estimated Time

**19-26 hours** of focused development work across all 7 plans.

## Execution Approaches

Each plan can be executed using one of two approaches:

### Option 1: Subagent-Driven Development (Recommended)
- Fresh subagent per task
- Automatic review between tasks
- Fast iteration with parallel execution where possible
- Use: `@superpowers:subagent-driven-development`

### Option 2: Inline Execution
- Execute tasks in current session
- Batch execution with checkpoints
- Use: `@superpowers:executing-plans`

## Plan Characteristics

All plans follow these principles:

- **Test-Driven Development (TDD):** Write tests first, then implementation
- **Bite-Sized Tasks:** Each task is 2-5 minutes of focused work
- **Frequent Commits:** Commit after each completed task
- **DRY & YAGNI:** Don't Repeat Yourself, You Aren't Gonna Need It
- **Complete Code:** All code snippets are production-ready, not pseudocode

## Technical Stack

- **Backend:** Django 6.0
- **Database:** SQLite (dev), PostgreSQL (production)
- **Storage:** Google Drive API (primary), Cloudinary (optional)
- **OCR:** Gemini API (primary), OpenRouter (optional)
- **Frontend:** Bootstrap 5, HTMX
- **Testing:** pytest, pytest-django, pytest-cov
- **Authentication:** Django built-in auth with role-based permissions

## Next Steps

1. **Choose execution approach** (subagent-driven or inline)
2. **Start with Plan 1** (Project Setup & Configuration)
3. **Execute plans sequentially** in the order listed above
4. **Each plan completion** enables the next plan to proceed
5. **All tests must pass** before moving to the next plan

## Notes

- Each plan includes a completion checklist at the end
- Plans reference the next plan in sequence
- All file paths are absolute and precise
- All commands include expected output
- Error handling and edge cases are covered

## Support

For questions or issues during implementation:
- Refer to the original spec: `docs/superpowers/specs/2026-03-14-budget-control-design.md`
- Each plan is self-contained with complete context
- Tests verify correctness at each step
