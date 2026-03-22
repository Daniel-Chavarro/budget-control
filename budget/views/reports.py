"""Report views for budget app."""
from django.shortcuts import render
from django.db.models import Sum, Count
from budget.decorators import admin_required
from budget.models import ExpenseData
from datetime import datetime, timedelta


@admin_required
def expense_report_view(request):
    """Detailed expense report with filtering."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category', '')
    
    expenses = ExpenseData.objects.filter(receipt__status='approved')
    
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    if category:
        expenses = expenses.filter(category=category)
    
    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_count = expenses.count()
    
    category_totals = expenses.values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    monthly_totals = []
    if expenses.exists():
        months = expenses.dates('date', 'month', order='DESC')[:12]
        for month in months:
            month_expenses = expenses.filter(date__year=month.year, date__month=month.month)
            monthly_totals.append({
                'month': month.strftime('%Y-%m'),
                'total': month_expenses.aggregate(t=Sum('amount'))['t'] or 0,
                'count': month_expenses.count()
            })
    
    context = {
        'expenses': expenses.select_related('receipt', 'receipt__uploaded_by')[:100],
        'total_amount': total_amount,
        'total_count': total_count,
        'category_totals': category_totals,
        'monthly_totals': monthly_totals,
        'start_date': start_date,
        'end_date': end_date,
        'selected_category': category,
        'categories': ExpenseData.CATEGORY_CHOICES,
    }
    
    return render(request, 'budget/reports/expense_report.html', context)
