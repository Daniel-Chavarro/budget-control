"""Receipt upload and management views."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from budget.decorators import any_authenticated_user
from budget.models import Receipt, ExpenseData
from budget.forms import ReceiptUploadForm, ExpenseDataForm
from budget.services import get_storage_service, get_ocr_service
from datetime import datetime


@any_authenticated_user
def receipt_upload_view(request):
    """Upload receipt with OCR processing."""
    upload_form = ReceiptUploadForm()
    expense_form = None
    receipt_url = None
    ocr_data = None
    
    if request.method == 'POST':
        if 'receipt_file' in request.FILES:
            # Step 1: Upload file
            upload_form = ReceiptUploadForm(request.POST, request.FILES)
            
            if upload_form.is_valid():
                file = upload_form.cleaned_data['receipt_file']
                
                # Determine uploader
                upload_as_user = upload_form.cleaned_data.get('upload_as_user')
                if upload_as_user and request.user.userprofile.is_admin:
                    uploader = upload_as_user
                else:
                    uploader = request.user
                
                # Upload to storage
                storage_service = get_storage_service()
                file_url = storage_service.upload_file(
                    file,
                    f'receipt_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{file.name}'
                )
                
                # Extract data with OCR
                ocr_service = get_ocr_service()
                file.seek(0)  # Reset file pointer
                ocr_data = ocr_service.extract_receipt_data(file)
                
                # Store receipt URL for display
                receipt_url = file_url
                
                # Prepare expense form with OCR data
                initial_data = {
                    'date': ocr_data.get('date') or datetime.now().date(),
                    'amount': ocr_data.get('amount') or '0.00',
                    'vendor': ocr_data.get('vendor') or '',
                    'category': ocr_data.get('category') or 'other',
                    'description': ocr_data.get('description') or '',
                }
                expense_form = ExpenseDataForm(initial=initial_data)
                
                # Store data in session for submission
                request.session['pending_receipt'] = {
                    'file_url': file_url,
                    'file_name': file.name,
                    'uploader_id': uploader.id,
                }
        
        elif 'submit_receipt' in request.POST:
            # Step 2: Submit receipt with expense data
            expense_form = ExpenseDataForm(request.POST)
            
            if expense_form.is_valid():
                pending_data = request.session.get('pending_receipt')
                
                if pending_data:
                    # Create receipt record
                    from django.contrib.auth.models import User
                    uploader = User.objects.get(id=pending_data['uploader_id'])
                    
                    receipt = Receipt.objects.create(
                        uploaded_by=uploader,
                        original_file_url=pending_data['file_url'],
                        file_name=pending_data['file_name'],
                        status='pending_review'
                    )
                    
                    # Create expense data
                    expense = expense_form.save(commit=False)
                    expense.receipt = receipt
                    expense.save()
                    
                    # Clear session
                    del request.session['pending_receipt']
                    
                    messages.success(request, 'Receipt uploaded successfully!')
                    return redirect('budget:receipt_list')
    
    # Show upload_as_user field only for admins
    if not request.user.userprofile.is_admin:
        upload_form.fields.pop('upload_as_user', None)
    
    context = {
        'upload_form': upload_form,
        'expense_form': expense_form,
        'receipt_url': receipt_url,
        'ocr_data': ocr_data,
    }
    
    return render(request, 'budget/receipts/upload.html', context)


@any_authenticated_user
def receipt_list_view(request):
    """List user's uploaded receipts."""
    if request.user.userprofile.is_admin:
        receipts = Receipt.objects.all()
    else:
        receipts = Receipt.objects.filter(uploaded_by=request.user)
    
    return render(request, 'budget/receipts/list.html', {'receipts': receipts})
