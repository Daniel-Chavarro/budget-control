# Upload Failure Handling Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When storage upload fails, warn user and keep form data so they can retry

**Architecture:** Wrap storage upload in try-catch, set session flag on failure, display warning messages both at top and inline

**Tech Stack:** Django views, Django messages framework, Jinja templates

---

## Files to Modify

1. `budget/views/receipts.py` - Add try-catch around upload, session flag
2. `budget/templates/budget/receipts/upload.html` - Add inline error indicator
3. `budget/templates/budget/base.html` - Add warning alert style

---

## Chunk 1: View Changes

### Task 1: Modify receipts view to catch upload errors

**Files:**
- Modify: `budget/views/receipts.py:165-210`

- [ ] **Step 1: Read current code around line 165**

```python
# Current code around line 168-170:
storage_service = get_storage_service()
storage_filename = f'receipt_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{file_name}'
file_url = storage_service.upload_file(file_content, storage_filename)
```

- [ ] **Step 2: Wrap in try-except**

Replace lines 168-170 with:

```python
                    storage_service = get_storage_service()
                    storage_filename = f'receipt_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{file_name}'
                    
                    try:
                        file_url = storage_service.upload_file(file_content, storage_filename)
                        logger.info(f"[RECEIPT SUBMIT] Storage upload successful: {file_url}")
                    except Exception as e:
                        logger.error(f"[RECEIPT SUBMIT] Storage upload failed: {str(e)}")
                        request.session['upload_error'] = True
                        messages.warning(request, 'Error uploading file to storage. Please check configuration or try again.')
                        transaction_form = TransactionForm(request.POST, instance=receipt, receipt_type=receipt_type)
                        return render(request, 'budget/receipts/upload.html', {
                            'upload_form': upload_form,
                            'transaction_form': transaction_form,
                            'receipt_url': receipt_url,
                            'ocr_data': ocr_data,
                            'has_pending': True,
                            'receipt_type_display': receipt_type,
                            'upload_error': True,
                            'time_remaining': time_remaining,
                        })
```

- [ ] **Step 3: Add upload_error to session clearing on success**

Find where `del request.session['pending_receipt']` is (around line 198), and ensure we also clear `upload_error`:

```python
                    del request.session['pending_receipt']
                    if 'upload_error' in request.session:
                        del request.session['upload_error']
```

---

## Chunk 2: Template Changes

### Task 2: Add inline error indicator to upload form

**Files:**
- Modify: `budget/templates/budget/receipts/upload.html`

- [ ] **Step 1: Read the template to find where to add error indicator**

Look for the form submission area (around submit button).

- [ ] **Step 2: Add inline error indicator**

Add after the form or near submit button:

```html
{% if upload_error %}
<div class="alert alert-warning mt-3">
    <i class="bi bi-exclamation-triangle me-2"></i>
    <strong>Upload failed:</strong> The file could not be saved to cloud storage. Please check configuration and try again.
</div>
{% endif %}
```

---

## Chunk 3: Add Warning Alert Style

### Task 3: Ensure warning alert style exists

**Files:**
- Modify: `budget/templates/budget/base.html`

- [ ] **Step 1: Check if .alert-warning exists**

Search for `.alert-warning` in base.html. If not found, add:

```css
.alert-warning {
    background: #fff3cd;
    color: #856404;
}
```

---

## Chunk 4: Testing

### Task 4: Test the implementation

- [ ] **Step 1: Test with invalid Cloudinary URL**

Set CLOUDINARY_URL to invalid value, try to upload a receipt.

Expected: Warning message appears, form data preserved, can retry

- [ ] **Step 2: Test successful upload still works**

Reset CLOUDINARY_URL to valid, upload receipt.

Expected: Success message, redirected to list

- [ ] **Step 3: Run existing tests**

```bash
pytest budget/tests/ -v
```

---

## Completion Criteria

1. Upload failure shows warning at top of page
2. Upload failure shows inline error in form
3. Form data is preserved after failure (can retry)
4. Successful upload still works as before
5. All existing tests pass
