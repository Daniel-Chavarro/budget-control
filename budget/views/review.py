"""Admin review workflow views."""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from budget.decorators import admin_required
from budget.models import Receipt
from budget.forms import TransactionForm

logger = logging.getLogger(__name__)


@admin_required
def pending_receipts_view(request):
    """List all pending receipts for review."""
    pending_receipts = Receipt.objects.filter(status='pendiente')
    logger.debug(f"[REVIEW] Admin {request.user} viewing pending receipts, count: {pending_receipts.count()}")
    return render(request, 'budget/review/pending_list.html', {
        'pending_receipts': pending_receipts
    })


@admin_required
def receipt_detail_view(request, pk):
    """Detailed receipt review page."""
    receipt = get_object_or_404(Receipt, pk=pk)
    logger.debug(f"[REVIEW] Admin {request.user} viewing receipt detail: {receipt.file_name}")
    
    if request.method == 'POST':
        action = request.POST.get('action')
        logger.debug(f"[REVIEW] Action received: {action} for receipt {receipt.id}")
        
        if action == 'approve':
            form = TransactionForm(request.POST, instance=receipt, receipt_type=receipt.receipt_type)
            
            if form.is_valid():
                transaction = form.save(commit=False)
                receipt.date = transaction.date
                receipt.amount = transaction.amount
                receipt.counterparty = transaction.counterparty
                receipt.category = transaction.category
                receipt.description = transaction.description
                receipt.modified_by_user = True
                
                receipt.status = 'aprobado'
                receipt.reviewed_by = request.user
                receipt.review_timestamp = timezone.now()
                receipt.review_notes = request.POST.get('review_notes', '')
                receipt.save()
                
                logger.info(f"[REVIEW] Receipt {receipt.id} APPROVED by {request.user}")
                messages.success(request, f'Recibo {receipt.file_name} aprobado.')
                return redirect('budget:pending_receipts')
        
        elif action == 'reject':
            notes = request.POST.get('review_notes', '')
            logger.debug(f"[REVIEW] Rejection notes: {notes[:50]}...")
            
            if not notes:
                logger.warning(f"[REVIEW] Rejection rejected - no notes provided")
                messages.error(request, 'Notas de rechazo son requeridas.')
            else:
                receipt.status = 'rechazado'
                receipt.reviewed_by = request.user
                receipt.review_timestamp = timezone.now()
                receipt.review_notes = notes
                receipt.save()
                
                logger.info(f"[REVIEW] Receipt {receipt.id} REJECTED by {request.user}")
                messages.success(request, f'Recibo {receipt.file_name} rechazado.')
                return redirect('budget:pending_receipts')
    
    form = TransactionForm(instance=receipt, receipt_type=receipt.receipt_type)
    
    context = {
        'receipt': receipt,
        'transaction_form': form,
    }
    
    return render(request, 'budget/review/detail.html', context)


@admin_required
def all_receipts_view(request):
    """List all receipts with filtering."""
    status_filter = request.GET.get('status', 'all')
    logger.debug(f"[REVIEW] Admin {request.user} viewing all receipts with filter: {status_filter}")
    
    receipts = Receipt.objects.all()
    if status_filter != 'all':
        receipts = receipts.filter(status=status_filter)
    
    return render(request, 'budget/review/all_receipts.html', {
        'receipts': receipts,
        'selected_status': status_filter
    })