# Upload Failure Handling Design

## Overview
When a file upload to cloud storage (Cloudinary, Google Drive) fails (e.g., invalid URL, authentication error), the application should not block user actions. Instead, it should warn the user and allow retry while preserving form data.

## Problem Statement
Currently, if storage upload fails during receipt submission, an exception is raised that crashes the flow or shows a technical error to the user. Users should be able to continue working with a warning message.

## Solution Approach 1: Try-catch in view with retry flag

### Changes Required

#### 1. Modify `budget/views/receipts.py`
- Wrap `storage_service.upload_file()` call in try-except
- On failure:
  - Set `upload_error` flag in session
  - Display warning message via Django messages
  - Do NOT clear pending_receipt from session (keep form data)
  - Render form with inline error indicator
- On success: existing behavior (clear session, redirect)

#### 2. Template changes (`budget/templates/bceipts/upload.html`)
- Add warning display at top (using Django messages with `warning` level)
- Add inline error indicator near submit area when `upload_error` is true
- Provide retry mechanism (re-submit button)

#### 3. Add warning message style
- Add `.alert-warning` style in base.html if not present

### Data Flow

```
User submits receipt form
       ↓
Storage upload attempted
       ↓
   [SUCCESS]              [FAILURE]
      ↓                      ↓
Clear session         Set upload_error=True
Redirect              Show warning message
                      Render form with error indicator
                      (User can retry)
```

### Session State

```python
# On upload failure, session contains:
{
    'pending_receipt': {
        'file_content': '...',
        'content_type': '...',
        'file_name': '...',
        'uploader_id': ...,
        'receipt_type': '...',
        'created_at': '...',
    },
    'upload_error': True  # NEW: flag to indicate error
}
```

### UI/UX

1. **Top alert**: Warning message "Error uploading file to storage. Please check configuration or try again."
2. **Inline indicator**: Red border or icon near the form indicating upload failed
3. **Retry**: User can click submit again to retry

### Error Handling

- Generic message shown to user: "Error uploading file. Please check storage configuration or contact administrator."
- Detailed error logged server-side for debugging

## Files to Modify

1. `budget/views/receipts.py` - Add try-catch around upload
2. `budget/templates/budget/receipts/upload.html` - Add error indicator
3. `budget/templates/budget/base.html` - Add warning alert style (if needed)

## Testing Considerations

- Test with invalid Cloudinary URL
- Test with invalid Google Drive credentials
- Verify session is preserved after failure
- Verify user can successfully retry after fixing configuration
