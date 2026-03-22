"""Admin review workflow views."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from budget.decorators import admin_required
from budget.models import Receipt, ExpenseData
from budget.forms import ExpenseDataForm


@admin_required
def pending_receipts_view(request):
    """List all pending receipts for review."""
    pending_receipts = Receipt.objects.filter(status='pending_review')
    return render(request, 'budget/review/pending_list.html', {
        'pending_receipts': pending_receipts
    })


@admin_required
def receipt_detail_view(request, pk):
    """Detailed receipt review page."""
    receipt = get_object_or_404(Receipt, pk=pk)
    
    try:
        expense_data = receipt.expense_data
    except ExpenseData.DoesNotExist:
        expense_data = None
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            if expense_data:
                form = ExpenseDataForm(request.POST, instance=expense_data)
            else:
                form = ExpenseDataForm(request.POST)
            
            if form.is_valid():
                expense = form.save(commit=False)
                if not expense_data:
                    expense.receipt = receipt
                expense.modified_by_user = True
                expense.save()
                
                receipt.status = 'approved'
                receipt.reviewed_by = request.user
                receipt.review_timestamp = timezone.now()
                receipt.review_notes = request.POST.get('review_notes', '')
                receipt.save()
                
                messages.success(request, f'Receipt {receipt.file_name} approved.')
                return redirect('budget:pending_receipts')
        
        elif action == 'reject':
            notes = request.POST.get('review_notes', '')
            
            if not notes:
                messages.error(request, 'Rejection notes are required.')
            else:
                receipt.status = 'rejected'
                receipt.reviewed_by = request.user
                receipt.review_timestamp = timezone.now()
                receipt.review_notes = notes
                receipt.save()
                
                messages.success(request, f'Receipt {receipt.file_name} rejected.')
                return redirect('budget:pending_receipts')
    
    if expense_data:
        expense_form = ExpenseDataForm(instance=expense_data)
    else:
        expense_form = ExpenseDataForm()
    
    context = {
        'receipt': receipt,
        'expense_form': expense_form,
    }
    
    return render(request, 'budget/review/detail.html', context)


@admin_required
def all_receipts_view(request):
    """List all receipts with filtering."""
    status_filter = request.GET.get('status', 'all')
    
    receipts = Receipt.objects.all()
    if status_filter != 'all':
        receipts = receipts.filter(status=status_filter)
    
    return render(request, 'budget/review/all_receipts.html', {
        'receipts': receipts,
        'status_filter': status_filter
    })
