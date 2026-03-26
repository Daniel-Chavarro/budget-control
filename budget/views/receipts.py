"""Receipt upload and management views."""
import base64
import logging

from PIL import Image
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from budget.decorators import any_authenticated_user, rate_limit
from budget.models import Receipt
from budget.forms import ReceiptUploadForm, TransactionForm, get_category_by_name_es
from budget.services import get_storage_service, get_ocr_service
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

PENDING_RECEIPT_EXPIRY_MINUTES = 10


def _is_pending_receipt_expired(pending_data):
    """Check if pending receipt session has expired."""
    if not pending_data:
        return True
    created_at = pending_data.get('created_at')
    if not created_at:
        return True
    try:
        created = datetime.fromisoformat(created_at)
        expiry = created + timedelta(minutes=PENDING_RECEIPT_EXPIRY_MINUTES)
        return datetime.now() > expiry
    except (ValueError, TypeError):
        return True


def _clear_pending_receipt(request):
    """Clear pending receipt from session."""
    if 'pending_receipt' in request.session:
        del request.session['pending_receipt']


@rate_limit(requests_per_minute=10, key_prefix='upload')
@any_authenticated_user
def receipt_upload_view(request):
    """Upload receipt with OCR processing - transactional upload."""
    pending_data = request.session.get('pending_receipt')
    if pending_data and _is_pending_receipt_expired(pending_data):
        _clear_pending_receipt(request)
        messages.info(request, 'La sesion de subida ha expirado. Por favor, sube el comprobante nuevamente.')
        pending_data = None
    
    is_admin = request.user.userprofile.is_admin
    upload_form = ReceiptUploadForm()
    transaction_form = None
    receipt_url = None
    ocr_data = None
    time_remaining = None
    
    if request.method == 'POST':
        if 'receipt_file' in request.FILES:
            logger.debug(f"[RECEIPT UPLOAD] User {request.user} initiating upload")
            
            upload_form = ReceiptUploadForm(request.POST, request.FILES)
            
            if upload_form.is_valid():
                file = upload_form.cleaned_data['receipt_file']
                logger.debug(f"[RECEIPT UPLOAD] File received: {file.name}, size: {file.size}")
                
                receipt_type = upload_form.cleaned_data.get('receipt_type', 'expense')
                if not is_admin:
                    receipt_type = 'income'
                
                upload_as_user = upload_form.cleaned_data.get('upload_as_user')
                if upload_as_user and is_admin:
                    uploader = upload_as_user
                    logger.debug(f"[RECEIPT UPLOAD] Admin uploading as: {uploader}")
                else:
                    uploader = request.user
                    logger.debug(f"[RECEIPT UPLOAD] Uploading as self: {uploader}")
                
                file_content = file.read()
                import io
                image = Image.open(io.BytesIO(file_content))
                
                content_type = file.content_type or 'image/jpeg'
                if content_type == 'image/jpeg':
                    mime_prefix = 'data:image/jpeg;base64,'
                elif content_type == 'image/png':
                    mime_prefix = 'data:image/png;base64,'
                elif 'pdf' in content_type:
                    mime_prefix = 'data:application/pdf;base64,'
                else:
                    mime_prefix = 'data:image/jpeg;base64,'

                logger.debug("[RECEIPT UPLOAD] Running OCR on temp file...")
                ocr_service = get_ocr_service()
                logger.debug(f"[RECEIPT UPLOAD] OCR provider: {type(ocr_service).__name__}")

                ocr_data = ocr_service.extract_receipt_data(image)
                logger.info(f"[RECEIPT UPLOAD] OCR extracted data: {ocr_data}")
                
                description = ocr_data.get('description') or ''
                if description.startswith('OCR failed:'):
                    description = ''
                
                category_name = ocr_data.get('category') or ''
                category_obj = get_category_by_name_es(category_name, receipt_type)
                category_id = category_obj.id if category_obj else None
                
                counterparty = ocr_data.get('vendor') or ''
                
                initial_data = {
                    'date': ocr_data.get('date') or datetime.now().date(),
                    'amount': ocr_data.get('amount') or '0.00',
                    'counterparty': counterparty,
                    'category': category_id,
                    'description': description,
                }
                logger.debug(f"[RECEIPT UPLOAD] Initial form data: {initial_data}")
                
                transaction_form = TransactionForm(initial=initial_data, receipt_type=receipt_type)
                
                request.session['pending_receipt'] = {
                    'file_content': base64.b64encode(file_content).decode('utf-8'),
                    'content_type': content_type,
                    'mime_prefix': mime_prefix,
                    'file_name': file.name,
                    'uploader_id': uploader.id,
                    'receipt_type': receipt_type,
                    'created_at': datetime.now().isoformat(),
                }
                logger.debug("[RECEIPT UPLOAD] Pending receipt stored in session (not yet uploaded)")
        
        elif 'submit_receipt' in request.POST:
            logger.debug(f"[RECEIPT SUBMIT] User {request.user} submitting receipt")
            
            pending_data = request.session.get('pending_receipt')
            if _is_pending_receipt_expired(pending_data):
                _clear_pending_receipt(request)
                messages.info(request, 'La sesion de subida ha expirado. Por favor, sube el comprobante nuevamente.')
                return redirect('budget:receipt_upload')
            
            if not is_admin:
                receipt_type = 'income'
            else:
                receipt_type = pending_data.get('receipt_type', 'expense') if pending_data else 'expense'
            
            receipt = Receipt()
            transaction_form = TransactionForm(request.POST, instance=receipt, receipt_type=receipt_type)
            
            if transaction_form.is_valid():
                pending_data = request.session.get('pending_receipt')
                logger.debug(f"[RECEIPT SUBMIT] Pending data from session: {pending_data}")
                
                if pending_data:
                    try:
                        file_content = base64.b64decode(pending_data['file_content'])
                    except Exception as e:
                        logger.error(f"[RECEIPT SUBMIT] Failed to decode file: {e}")
                        _clear_pending_receipt(request)
                        messages.error(request, 'Error al procesar el archivo. Por favor, sube el comprobante nuevamente.')
                        return redirect('budget:receipt_upload')
                    
                    file_name = pending_data['file_name']
                    uploader_id = pending_data['uploader_id']
                    receipt_type = pending_data.get('receipt_type', 'expense')
                    
                    logger.debug("[RECEIPT SUBMIT] Uploading file to permanent storage...")
                    storage_service = get_storage_service()
                    storage_filename = f'receipt_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{file_name}'
                    file_url = storage_service.upload_file(file_content, storage_filename)
                    logger.info(f"[RECEIPT SUBMIT] Storage upload successful: {file_url}")
                    
                    from django.contrib.auth.models import User
                    uploader = User.objects.get(id=uploader_id)
                    
                    receipt = Receipt.objects.create(
                        uploaded_by=uploader,
                        original_file_url=file_url,
                        file_name=file_name,
                        receipt_type=receipt_type,
                        status='pending_review'
                    )
                    logger.info(f"[RECEIPT SUBMIT] Receipt created: id={receipt.id}, file={receipt.file_name}, type={receipt_type}")
                    
                    transaction = transaction_form.save(commit=False)
                    transaction.id = receipt.id
                    transaction.modified_by_user = True
                    receipt.date = transaction.date
                    receipt.amount = transaction.amount
                    receipt.counterparty = transaction.counterparty
                    receipt.category = transaction.category
                    receipt.description = transaction.description
                    receipt.modified_by_user = True
                    receipt.save()
                    
                    logger.info(f"[RECEIPT SUBMIT] Transaction data saved: counterparty={transaction.counterparty}, amount={transaction.amount}")
                    
                    del request.session['pending_receipt']
                    logger.debug("[RECEIPT SUBMIT] Session cleared")
                    
                    messages.success(request, 'Comprobante subido exitosamente!')
                    return redirect('budget:receipt_list')
        
        elif 'cancel_receipt' in request.POST:
            logger.debug(f"[RECEIPT CANCEL] User {request.user} cancelled upload")
            _clear_pending_receipt(request)
            logger.debug("[RECEIPT CANCEL] Pending receipt cleared from session")
            messages.info(request, 'Subida cancelada.')
            return redirect('budget:receipt_upload')
    
    pending_data = request.session.get('pending_receipt')
    if pending_data:
        if _is_pending_receipt_expired(pending_data):
            _clear_pending_receipt(request)
            messages.info(request, 'La sesion de subida ha expirado. Por favor, sube el comprobante nuevamente.')
            pending_data = None
        else:
            created_at = datetime.fromisoformat(pending_data['created_at'])
            expiry = created_at + timedelta(minutes=PENDING_RECEIPT_EXPIRY_MINUTES)
            time_remaining = int((expiry - datetime.now()).total_seconds() / 60)
            mime_prefix = pending_data.get('mime_prefix', 'data:image/jpeg;base64,')
            receipt_url = f"{mime_prefix}{pending_data['file_content']}"
    
    if not is_admin:
        upload_form.fields.pop('upload_as_user', None)
        upload_form.fields['receipt_type'].widget = forms.HiddenInput()
        upload_form.initial['receipt_type'] = 'income'
    
    receipt_type_display = 'income'
    if is_admin:
        pending_data = request.session.get('pending_receipt')
        receipt_type_display = pending_data.get('receipt_type', 'expense') if pending_data else 'expense'
    
    context = {
        'upload_form': upload_form,
        'transaction_form': transaction_form,
        'receipt_url': receipt_url,
        'ocr_data': ocr_data,
        'has_pending': bool(pending_data),
        'receipt_type_display': receipt_type_display,
        'time_remaining': time_remaining if pending_data else None,
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