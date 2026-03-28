# Web Test Workflow Design

## Overview

Automated end-to-end tests using Playwright CLI to simulate real user workflows in the budget control web application. Tests verify all functionality works from a user perspective, including authentication, receipt management, admin review, and administrative functions.

## Goals

- Test all workflows end-to-end simulating real user interactions
- Verify server is running, start it if needed, stop it when done
- Reuse test database and users across test session
- Capture detailed evidence on failures (screenshots, logs)
- Generate comprehensive report with pass/fail status and categorization

## Architecture

### Test Structure

```
docs/test/
├── conftest.py                    # Shared fixtures and configuration
├── test_auth.py                   # Authentication workflows
├── test_receipt_upload.py         # Receipt upload and management
├── test_review.py                 # Admin review workflow
├── test_user_management.py        # User CRUD operations
├── test_category_management.py    # Category CRUD operations
├── test_reports.py                # Expense reports
└── utils/
    ├── __init__.py
    ├── server_manager.py          # Server lifecycle management
    └── test_fixtures.py           # Test data creation
```

### Components

**ServerManager**
- Checks if Django server running on localhost:8000
- Starts server via subprocess if not running
- Tracks PID for clean shutdown
- Provides context manager interface

**TestFixtures**
- Runs Django migrations once at session start
- Creates admin, tenant, unlinked_user fixtures
- Users persist across tests (reused)

**BrowserHelper**
- Playwright CLI wrapper for common operations
- Screenshot capture on failure
- Console log collection

## Test Workflows

### 1. Authentication (test_auth.py)

| Test | Description |
|------|-------------|
| admin_login_success | Admin logs in with valid credentials |
| admin_login_invalid_password | Admin login fails with wrong password |
| admin_login_nonexistent | Login fails for non-existent user |
| tenant_login_success | Tenant logs in successfully |
| register_new_user | New user registration |
| register_duplicate_email | Registration fails with existing email |
| logout_success | User logs out successfully |

### 2. Receipt Upload (test_receipt_upload.py)

| Test | Description |
|------|-------------|
| upload_receipt_as_tenant | Tenant uploads receipt successfully |
| upload_receipt_as_admin | Admin uploads expense receipt |
| upload_empty_file | Upload fails with empty file |
| upload_oversized_file | Upload fails with file > 10MB |
| upload_invalid_format | Upload fails with unsupported format |
| receipt_list_tenant | Tenant sees only their receipts |
| receipt_list_admin | Admin sees all receipts |
| cancel_upload | User cancels upload mid-process |

### 3. Admin Review (test_review.py)

| Test | Description |
|------|-------------|
| pending_receipts_list | Admin sees pending receipts |
| approve_receipt | Admin approves receipt successfully |
| reject_receipt | Admin rejects receipt with notes |
| reject_without_notes | Rejection fails without notes |
| edit_before_approve | Admin edits data before approval |
| all_receipts_filter | Filter by status works |
| tenant_cannot_access_review | Tenant blocked from review pages |

### 4. User Management (test_user_management.py)

| Test | Description |
|------|-------------|
| user_list | Admin views user list |
| create_user | Admin creates new user |
| delete_user | Admin deletes user |
| edit_user | Admin edits user details |
| tenant_cannot_access | Tenant blocked from user management |

### 5. Category Management (test_category_management.py)

| Test | Description |
|------|-------------|
| category_list | Admin views categories |
| create_category | Admin creates category |
| edit_category | Admin edits category |
| delete_category | Admin deletes category |

### 6. Reports (test_reports.py)

| Test | Description |
|------|-------------|
| expense_report_load | Report page loads |
| expense_report_by_date | Filter by date range works |
| expense_report_by_category | Filter by category works |

## Server Management

### Startup Flow

1. Check localhost:8000 with HTTP HEAD request
2. If response != 200, start server:
   - `subprocess.Popen(['python', 'manage.py', 'runserver', '8000'])`
   - Wait for server ready (poll with retry, 5s timeout)
3. If already running, use existing server

### Shutdown Flow

1. On test session complete (not between tests)
2. Terminate server process by PID
3. Wait for port release

### Database Setup

1. Run `python manage.py migrate` once at session start
2. Create test users via Django ORM:
   - `admin` / `adminpass123` (role: admin)
   - `tenant1` / `tenantpass123` (role: tenant)
   - `unlinked1` / `unlinkedpass123` (role: unlinked)

## Reporting

### Output Location

`docs/test/2026-03-28-web-test-workflow.md`

### Report Sections

#### 1. What Works
- List of tests that passed
- Brief description of what was verified

#### 2. What Doesn't Work
- Failed tests with:
  - Test name and description
  - Screenshot of failure
  - Console errors (if any)
  - Expected vs actual behavior

#### 3. Might Fail / Clarification Needed
- Timing-dependent tests that may be flaky
- Edge cases with ambiguous requirements
- Tests that depend on external services
- Questions for product owner

### Screenshot Naming

```
docs/test/screenshots/
├── test_auth_admin_login_success.png
├── test_auth_admin_login_invalid_password.png
└── ...
```

## Execution

### Run All Tests

```bash
cd docs/test
pytest -v --tb=short
```

### Run Specific Suite

```bash
pytest test_auth.py -v
```

### With Coverage

```bash
pytest --cov=budget --cov-report=html
```

## Dependencies

- pytest
- playwright-cli
- Django (for migrations)

## Notes

- Tests run against SQLite database (development)
- Server runs on localhost:8000
- Browser: Chromium (default for playwright-cli)
- Each test is independent but shares browser context
- Screenshots captured only on test failures
