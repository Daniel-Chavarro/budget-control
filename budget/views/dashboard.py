"""Dashboard views for budget app."""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from budget.models import Receipt
from datetime import datetime


@login_required
def dashboard_view(request):
    """Role-based dashboard router."""
    if request.user.userprofile.is_admin:
        return admin_dashboard(request)
    else:
        return tenant_dashboard(request)


def tenant_dashboard(request):
    """Dashboard for tenant and unlinked users."""
    user = request.user
    
    now = datetime.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    month_total = Receipt.objects.filter(
        status='approved',
        receipt_type='income',
        uploaded_by=user,
        date__gte=this_month_start
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    year_total = Receipt.objects.filter(
        status='approved',
        receipt_type='income',
        uploaded_by=user,
        date__gte=this_year_start
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    my_receipts = Receipt.objects.filter(
        uploaded_by=user
    ).order_by('-upload_timestamp')[:10]
    
    recent_incomes = Receipt.objects.filter(
        status='approved',
        receipt_type='income',
        uploaded_by=user
    ).order_by('-date')[:10]
    
    context = {
        'month_total': month_total,
        'year_total': year_total,
        'my_receipts': my_receipts,
        'recent_incomes': recent_incomes,
    }
    
    return render(request, 'budget/dashboard/tenant.html', context)


def admin_dashboard(request):
    """Dashboard for admin users."""
    pending_count = Receipt.objects.filter(status='pending_review').count()
    approved_count = Receipt.objects.filter(status='approved').count()
    rejected_count = Receipt.objects.filter(status='rejected').count()
    total_users = User.objects.count()
    
    now = datetime.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    month_expenses = Receipt.objects.filter(
        status='approved',
        receipt_type='expense',
        date__gte=this_month_start
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    month_incomes = Receipt.objects.filter(
        status='approved',
        receipt_type='income',
        date__gte=this_month_start
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    expense_category_breakdown = Receipt.objects.filter(
        status='approved',
        receipt_type='expense'
    ).values('category__name', 'category__name_es').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    income_category_breakdown = Receipt.objects.filter(
        status='approved',
        receipt_type='income'
    ).values('category__name', 'category__name_es').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    recent_receipts = Receipt.objects.all().order_by('-upload_timestamp')[:10]
    
    pending_receipts = Receipt.objects.filter(
        status='pending_review'
    ).select_related('uploaded_by')[:5]
    
    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_users': total_users,
        'month_expenses': month_expenses,
        'month_incomes': month_incomes,
        'expense_category_breakdown': expense_category_breakdown,
        'income_category_breakdown': income_category_breakdown,
        'recent_receipts': recent_receipts,
        'pending_receipts': pending_receipts,
    }
    
    return render(request, 'budget/dashboard/admin.html', context)