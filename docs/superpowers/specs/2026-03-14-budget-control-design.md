# Budget Control System Design

**Date:** 2026-03-14  
**Status:** Approved  
**Project:** Apartment Administration Budget Control

---

## 1. Overview

A budget control system for apartment building administration where tenants upload receipts for common area expenses, data is auto-extracted via OCR, and admins review/approve payments.

### Purpose
- Enable tenants to upload receipts for common area expenses
- Automatically extract receipt data using OCR (Gemini/OpenRouter)
- Provide admin approval workflow for fraud prevention
- Track and report on building expenses

### User Roles

| Role | Description |
|------|-------------|
| Admin | Full system access, approve/reject receipts, manage users/units, view all data |
| Tenant | Upload receipts, view approved expenses (summary + list), linked to apartment/parking |
| Unlinked User | Pays for parking slots but doesn't live in building |

### Unit Types
- **Apartment** - Residential units
- **Public Parking** - Rentable parking slots (private parking is not tracked)

---

## 2. Architecture

### Approach
Monolithic Django with traditional server-side rendering, enhanced with HTMX for interactive receipt upload/preview.

### Django App Structure (Single App)

```
budget-control/
├── core/                     # Project settings (existing)
│   ├── settings/
│   │   ├── base.py           # Common settings
│   │   ├── development.py    # Dev overrides
│   │   └── production.py     # Production settings
│   └── urls.py               # Root URL configuration
│
└── budget/                   # Single app (python manage.py startapp budget)
    ├── models/
    │   ├── __init__.py       # Import all models here
    │   ├── user.py           # UserProfile model
    │   ├── unit.py           # Unit, UserUnit models
    │   └── receipt.py        # Receipt, ExpenseData models
    │
    ├── views/
    │   ├── __init__.py
    │   ├── auth.py           # Login, logout, registration
    │   ├── dashboard.py      # Role-based dashboards
    │   ├── receipts.py       # Upload, list, detail views
    │   ├── review.py         # Admin review workflow
    │   └── management.py     # User/unit management (admin)
    │
    ├── services/
    │   ├── __init__.py
    │   ├── ocr_service.py    # OCR abstraction layer
    │   └── storage_service.py # Storage abstraction layer
    │
    ├── forms/
    │   ├── __init__.py
    │   ├── auth_forms.py     # Login, registration forms
    │   ├── receipt_forms.py  # Upload, expense data forms
    │   └── management_forms.py # User/unit forms
    │
    ├── templates/
    │   └── budget/
    │       ├── base.html     # Base layout
    │       ├── auth/         # Login, register templates
    │       ├── dashboard/    # Dashboard templates
    │       ├── receipts/     # Receipt upload/list templates
    │       ├── review/       # Admin review templates
    │       └── management/   # User/unit management templates
    │
    ├── static/
    │   └── budget/
    │       ├── css/
    │       └── js/
    │
    ├── templatetags/         # Custom template tags if needed
    ├── admin.py              # Django admin customization
    ├── urls.py               # App URL patterns
    └── tests/
        ├── test_models.py
        ├── test_views.py
        └── test_services.py
```

### Key Technologies
- **Backend:** Django 6.0, Django Forms, Django ORM
- **Database:** SQLite (dev), PostgreSQL (production)
- **File Storage:** Google Drive API (primary), Cloudinary (upgrade option)
- **OCR Service:** Gemini API (primary), OpenRouter (swappable)
- **Frontend Enhancement:** HTMX for async interactions
- **Authentication:** Django built-in auth with role-based permissions

---

## 3. Data Models

### User Model (extends Django User)
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    role = models.CharField(choices=['admin', 'tenant', 'unlinked_user'])
    phone = models.CharField(max_length=20, blank=True)
```

### Unit Model
```python
class Unit(models.Model):
    type = models.CharField(choices=['apartment', 'public_parking'])
    identifier = models.CharField(max_length=50)  # Unit number/name
    status = models.CharField(choices=['active', 'inactive'])
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True)
```

### UserUnit (many-to-many relationship)
```python
class UserUnit(models.Model):
    user = models.ForeignKey(User)
    unit = models.ForeignKey(Unit)
    role_in_unit = models.CharField(choices=['owner', 'tenant', 'authorized_user'])
    start_date = models.DateField()
    end_date = models.DateField(null=True)
```

### Receipt Model
```python
class Receipt(models.Model):
    uploaded_by = models.ForeignKey(User, related_name='uploaded_receipts')
    original_file_url = models.URLField()  # Google Drive link
    file_name = models.CharField(max_length=255)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=['pending_review', 'approved', 'rejected'])
    reviewed_by = models.ForeignKey(User, null=True, related_name='reviewed_receipts')
    review_timestamp = models.DateTimeField(null=True)
    review_notes = models.TextField(blank=True)
```

### ExpenseData Model
```python
class ExpenseData(models.Model):
    receipt = models.OneToOneField(Receipt)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    vendor = models.CharField(max_length=200)
    category = models.CharField(choices=[
        'maintenance', 'utilities', 'cleaning', 
        'security', 'repairs', 'other'
    ])
    description = models.TextField(blank=True)
    modified_by_user = models.BooleanField(default=False)
```

---

## 4. Core Workflows

### Tenant Receipt Upload Flow
1. Tenant navigates to "Upload Receipt" page
2. Selects image/PDF file (drag-drop or file picker)
3. File uploads to Google Drive via API
4. System calls OCR service (Gemini/OpenRouter) with image
5. OCR extracts: date, amount, vendor, category, description
6. Single-page form displays with:
   - Receipt preview (image from Google Drive)
   - Editable fields pre-filled with OCR data
   - Category dropdown
   - Submit button
7. Tenant reviews/edits data, clicks Submit
8. Receipt saved with status="pending_review"
9. Confirmation message shown

### Admin Receipt Upload Flow
1. Admin can upload as themselves OR impersonate another user
2. Upload page has "Upload as" dropdown (defaults to admin)
3. Same OCR extraction flow as tenants
4. If uploaded as admin: can directly mark as "approved" during upload OR submit for review
5. If uploaded as another user: follows tenant flow (pending_review)

### Admin Review Flow
1. Admin views "Pending Receipts" list
2. Clicks on a receipt to review
3. Detailed review page shows:
   - Original receipt image (from Google Drive)
   - Extracted data fields (with edit capability)
   - Submitter info and timestamp
   - Approve/Reject buttons
   - Notes field (required for rejection)
4. Admin can edit expense data before approving
5. Admin clicks Approve or Reject
6. Status updated, timestamp recorded
7. Submitter notified (optional)

### Tenant Dashboard
- Summary totals: total approved common expenses (monthly/yearly)
- List of approved expenses with: date, vendor, category, amount
- My Receipts section (status, date, amount)
- Linked units section

### Admin Dashboard
- All receipts (pending, approved, rejected) with filtering
- Detailed expense reports and analytics
- User/unit management
- Upload receipt button (with user selection)

---

## 5. External Service Abstractions

### OCR Service Layer
```python
# budget/services/ocr_service.py

class BaseOCRService:
    def extract_receipt_data(self, image_file) -> dict:
        """Returns: {date, amount, vendor, category, description, confidence}"""
        raise NotImplementedError

class GeminiOCRService(BaseOCRService):
    def extract_receipt_data(self, image_file) -> dict:
        # Implementation using Gemini API
        pass

class OpenRouterOCRService(BaseOCRService):
    def extract_receipt_data(self, image_file) -> dict:
        # Implementation using OpenRouter API
        pass

def get_ocr_service() -> BaseOCRService:
    if settings.OCR_PROVIDER == 'gemini':
        return GeminiOCRService()
    elif settings.OCR_PROVIDER == 'openrouter':
        return OpenRouterOCRService()
```

### Storage Service Layer
```python
# budget/services/storage_service.py

class BaseStorageService:
    def upload_file(self, file, filename) -> str:
        """Returns: URL to uploaded file"""
        raise NotImplementedError

class GoogleDriveStorage(BaseStorageService):
    def upload_file(self, file, filename) -> str:
        # Implementation using Google Drive API
        pass

class CloudinaryStorage(BaseStorageService):
    def upload_file(self, file, filename) -> str:
        # Implementation using Cloudinary API
        pass

def get_storage_service() -> BaseStorageService:
    if settings.STORAGE_PROVIDER == 'google_drive':
        return GoogleDriveStorage()
    elif settings.STORAGE_PROVIDER == 'cloudinary':
        return CloudinaryStorage()
```

---

## 6. Security & Permissions

### Authentication
- Django's built-in authentication system
- Required login for all pages (except login/register)
- Session-based authentication

### Authorization Rules

| Action | Admin | Tenant                | Unlinked User |
|--------|-------|-----------------------|---------------|
| View all receipts | Yes | Not sure, possibly yes | No |
| Approve/reject receipts | Yes | No                    | No |
| Edit any expense data | Yes | No                    | No |
| Upload as any user | Yes | No                    | No |
| Manage users/units | Yes | No                    | No |
| View detailed reports | Yes | No                    | No |
| Upload own receipts | Yes | Yes                   | Yes |
| Edit own pending receipts | Yes | Yes                   | Yes |
| View approved expenses | Yes | Summary + List        | Summary + List |
| View own submissions | Yes | Yes                   | Yes |

### File Security
- Google Drive files stored in service account folder (not public)
- Access URLs require authentication
- File validation: max size (10MB), allowed types (jpg, png, pdf)
- Malware scanning consideration for production

### CSRF Protection
- Django's built-in CSRF middleware for all forms

---

## 7. Error Handling

### OCR Failures
- If OCR API fails/times out: Show error, save receipt with empty expense data
- User can manually fill all fields
- Retry button available for OCR extraction

### File Upload Failures
- Google Drive API errors: Show friendly error message, allow retry
- Network issues: Client-side retry logic with exponential backoff
- File validation failures: Clear error messages (file too large, wrong format)

### Data Validation
- Amount: Must be positive decimal, max 2 decimal places
- Date: Cannot be future date, reasonable past range (within 2 years)
- Vendor: Required field, max 200 characters
- Category: Must be from predefined list
- Server-side validation on all submissions

### Google Drive Quotas
- Monitor storage usage
- Implement file cleanup for rejected receipts (optional, after X days)
- Alert admins when approaching quota limits

### OCR Extraction Quality
- Flag low-confidence extractions (if API provides confidence scores)
- Always allow manual override
- Track edit rate to monitor OCR quality

### Concurrent Edits
- Timestamp-based conflict detection for admin edits
- Last write wins with warning if data was modified

---

## 8. User Interface

### Page Structure

**Common Layout:**
- Navigation bar: Logo, Dashboard, Upload Receipt (tenants), Pending Receipts (admins), Units (admins), Users (admins), Profile, Logout
- Role indicator showing current user's role
- Responsive design (mobile-friendly)

**Upload Receipt Page:**
- File dropzone with preview
- Progress indicator during upload
- OCR processing spinner
- Form with fields (date, amount, vendor, category, description)
- Side-by-side layout: receipt image on left, form on right (desktop)
- Stacked on mobile
- Clear success/error messages

**Admin Review Page:**
- Receipt image display (zoomable)
- Expense data in editable fields
- Submitter information card
- Review history if previously reviewed
- Approve/Reject buttons (prominent)
- Notes textarea (required for rejection)
- Back to list button

**Tenant Dashboard:**
- Summary cards: Total expenses this month, this year
- Table of approved expenses (sortable, filterable)
- My Receipts section (status, date, amount)
- Linked units section

**Admin Dashboard:**
- Statistics cards: pending count, approved this month, rejected count
- Pending receipts table (priority view)
- All receipts table with status filters
- Quick actions: Upload receipt, Manage users

### Visual Feedback
- Loading states for async operations
- Success/error toast notifications
- Form validation highlights
- Status badges (pending/approved/rejected with colors)

---

## 9. Testing Strategy

### Testing Approach
- **Unit Tests:** Models, forms, services (OCR, storage abstractions)
- **Integration Tests:** Upload workflow, approval workflow, user permissions
- **Manual Testing:** OCR quality with real receipts, file upload edge cases
- **Test Data:** Sample receipts (images/PDFs) for development

### Key Test Scenarios
- Upload with valid/invalid files
- OCR extraction accuracy
- User permission boundaries (tenant can't access admin features)
- Receipt approval/rejection flows
- Google Drive API failure handling
- Multi-user scenarios (shared apartments)

---

## 10. Configuration

### Environment Variables
```
# OCR Provider
OCR_PROVIDER=gemini  # or 'openrouter'
GEMINI_API_KEY=xxx
OPENROUTER_API_KEY=xxx

# Storage Provider
STORAGE_PROVIDER=google_drive  # or 'cloudinary'
GOOGLE_DRIVE_CREDENTIALS_FILE=xxx
CLOUDINARY_URL=xxx

# Django
SECRET_KEY=xxx
DEBUG=False
DATABASE_URL=xxx
```

### Settings Structure
- `core/settings/base.py` - Common settings
- `core/settings/development.py` - Development overrides
- `core/settings/production.py` - Production settings

---

## 11. Future Enhancements (Out of Scope for V1)

- Email notifications for receipt status changes
- Expense analytics and charts
- Export reports to PDF/Excel
- Mobile app
- Recurring expense templates
- Multi-building support
- Payment tracking integration

---

## 12. Deployment Considerations

- Database migration to PostgreSQL for production
- Static file serving (WhiteNoise or CDN)
- Environment variable management
- Google Drive service account setup
- API key security
