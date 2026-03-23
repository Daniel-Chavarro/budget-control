"""Report views for budget app."""
from django.shortcuts import render
from django.db.models import Sum, Count
from budget.decorators import admin_required
from budget.models import Receipt, Category


@admin_required
def expense_report_view(request):
    """Detailed expense/income report with filtering."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category_id = request.GET.get('category', '')
    report_type = request.GET.get('type', 'all')
    
    expense_categories = Category.objects.filter(category_type='expense', is_active=True).order_by('name_es')
    income_categories = Category.objects.filter(category_type='income', is_active=True).order_by('name_es')
    
    receipts = Receipt.objects.filter(status='approved')
    
    if start_date:
        receipts = receipts.filter(date__gte=start_date)
    if end_date:
        receipts = receipts.filter(date__lte=end_date)
    
    expenses = receipts.filter(receipt_type='expense')
    incomes = receipts.filter(receipt_type='income')
    
    expense_category_totals = expenses.values('category__name', 'category__name_es').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    income_category_totals = incomes.values('category__name', 'category__name_es').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_incomes = incomes.aggregate(total=Sum('amount'))['total'] or 0
    balance = total_incomes - total_expenses
    
    context = {
        'expenses': expenses.select_related('uploaded_by', 'category')[:100] if report_type in ['all', 'expense'] else [],
        'incomes': incomes.select_related('uploaded_by', 'category')[:100] if report_type in ['all', 'income'] else [],
        'total_expenses': total_expenses,
        'total_incomes': total_incomes,
        'balance': balance,
        'expense_category_totals': expense_category_totals,
        'income_category_totals': income_category_totals,
        'expense_categories': expense_categories,
        'income_categories': income_categories,
        'start_date': start_date,
        'end_date': end_date,
        'selected_type': report_type,
        'selected_category': category_id,
    }
    
    return render(request, 'budget/reports/expense_report.html', context)