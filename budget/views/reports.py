"""Report views for budget app."""
from django.shortcuts import render
from django.db.models import Sum, Count
from budget.decorators import admin_required
from budget.models import ExpenseData, IncomeData, Category
from datetime import datetime, timedelta


@admin_required
def expense_report_view(request):
    """Detailed expense/income report with filtering."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category_id = request.GET.get('category', '')
    report_type = request.GET.get('type', 'all')
    
    expense_categories = Category.objects.filter(category_type='expense', is_active=True).order_by('name_es')
    income_categories = Category.objects.filter(category_type='income', is_active=True).order_by('name_es')
    
    expenses = ExpenseData.objects.filter(receipt__status='approved').select_related('category')
    incomes = IncomeData.objects.filter(receipt__status='approved').select_related('category')
    
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
        incomes = incomes.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
        incomes = incomes.filter(date__lte=end_date)
    
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
    expense_count = expenses.count()
    income_count = incomes.count()
    
    if report_type == 'expense':
        items = expenses.select_related('receipt', 'receipt__uploaded_by', 'category')[:100]
        categories = expense_categories
    elif report_type == 'income':
        items = incomes.select_related('receipt', 'receipt__uploaded_by', 'category')[:100]
        categories = income_categories
    else:
        items = None
        categories = expense_categories
    
    context = {
        'items': items,
        'expenses': expenses.select_related('receipt', 'receipt__uploaded_by', 'category')[:100] if report_type in ['all', 'expense'] else [],
        'incomes': incomes.select_related('receipt', 'receipt__uploaded_by', 'category')[:100] if report_type in ['all', 'income'] else [],
        'total_expenses': total_expenses,
        'total_incomes': total_incomes,
        'expense_count': expense_count,
        'income_count': income_count,
        'expense_category_totals': expense_category_totals,
        'income_category_totals': income_category_totals,
        'monthly_totals': [],
        'start_date': start_date,
        'end_date': end_date,
        'selected_category': category_id,
        'selected_type': report_type,
        'expense_categories': expense_categories,
        'income_categories': income_categories,
        'balance': balance,
    }
    
    return render(request, 'budget/reports/expense_report.html', context)
