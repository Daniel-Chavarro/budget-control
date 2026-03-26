# Budget Control System

A budget control system for apartment building administration where tenants upload receipts for common area expenses, data is auto-extracted via OCR, and admins review/approve payments.

## Features

- **Role-based access control**: Admin, Tenant, and Unlinked User roles
- **Receipt upload with OCR**: Automatic data extraction using Gemini or OpenRouter
- **Admin review workflow**: Approve/reject receipts with notes
- **Unit management**: Track apartments and parking slots
- **Expense reporting**: View approved expenses by date range and category
- **Cloud storage**: Google Drive or Cloudinary integration

## Tech Stack

- **Backend**: Django 6.0
- **Database**: SQLite (dev), PostgreSQL (production)
- **OCR**: Gemini API or OpenRouter (swappable)
- **Storage**: Google Drive API or Cloudinary
- **Frontend**: Bootstrap 5 with HTMX for async interactions

## Quick Start

### 1. Clone and Setup Virtual Environment

```bash
git clone <repository-url>
cd budget-control
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements/development.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```
SECRET_KEY=your-secret-key-here
DEBUG=True

# Storage (optional - defaults to google_drive)
STORAGE_PROVIDER=google_drive
GOOGLE_DRIVE_CREDENTIALS_FILE=path/to/credentials.json
# or
STORAGE_PROVIDER=cloudinary
CLOUDINARY_URL=cloudinary://...

# OCR (optional - defaults to gemini)
OCR_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
# or
OCR_PROVIDER=openrouter
OPENROUTER_API_KEY=your-openrouter-api-key
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Admin User

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` and log in with your admin credentials.

## User Roles

| Role | Description |
|------|-------------|
| **Admin** | Full system access, approve/reject receipts, manage users/units |
| **Tenant** | Upload receipts, view approved expenses, linked to apartment |
| **Unlinked User** | Pays for parking slots but doesn't live in building |

## Workflows

### Tenant Receipt Upload

1. Navigate to "Upload Receipt"
2. Select image/PDF file (max 10MB)
3. System uploads to storage and runs OCR
4. Review/edit extracted data
5. Submit for admin review

### Admin Review

1. View pending receipts in dashboard
2. Click receipt to review details
3. Edit data if needed
4. Approve or reject with notes

## Project Structure

```
budget-control/
├── core/                     # Project settings
│   ├── settings/
│   │   ├── base.py          # Common settings
│   │   ├── development.py   # Dev overrides
│   │   └── production.py    # Production settings
│   └── urls.py              # Root URLs
│
├── budget/                   # Main application
│   ├── models/              # Database models
│   │   ├── user.py          # UserProfile
│   │   ├── unit.py          # Unit, UserUnit
│   │   └── receipt.py       # Receipt, ExpenseData
│   ├── views/               # View functions
│   ├── forms/               # Form classes
│   ├── services/            # External services
│   │   ├── ocr_service.py   # OCR abstraction
│   │   └── storage_service.py
│   ├── templates/budget/    # HTML templates
│   ├── tests/               # Test suite
│   └── urls.py              # App URLs
│
├── requirements/
│   ├── base.txt             # Core dependencies
│   ├── development.txt      # Dev dependencies
│   └── production.txt       # Production dependencies
│
├── .env                      # Environment variables (git-ignored)
├── .env.example             # Environment template
├── manage.py
└── pytest.ini
```

## Testing

Run the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=budget --cov-report=html
```

View coverage report:

```bash
open htmlcov/index.html
```

## Production Deployment

1. Install production dependencies:
   ```bash
   pip install -r requirements/production.txt
   ```

2. Set environment variables:
   ```bash
   export DEBUG=False
   export SECRET_KEY=your-secret-key
   export DB_NAME=dbname
   export DB_USER=user
   export DB_PASSWORD=pass
   export DB_HOST=host
   export DB_PORT=5432
   ```

3. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

4. Run with gunicorn:
   ```bash
   gunicorn core.wsgi:application
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (insecure default) |
| `DEBUG` | Debug mode | `False` |
| `DB_NAME` | PostgreSQL database name | - |
| `DB_USER` | PostgreSQL username | - |
| `DB_PASSWORD` | PostgreSQL password | - |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `STORAGE_PROVIDER` | `google_drive` or `cloudinary` | `google_drive` |
| `GOOGLE_DRIVE_CREDENTIALS_FILE` | Path to credentials JSON | - |
| `CLOUDINARY_URL` | Cloudinary connection URL | - |
| `OCR_PROVIDER` | `gemini` or `openrouter` | `gemini` |
| `GEMINI_API_KEY` | Gemini API key | - |
| `OPENROUTER_API_KEY` | OpenRouter API key | - |

## License

MIT
