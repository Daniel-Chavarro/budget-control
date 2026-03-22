"""Budget app views."""
from django.shortcuts import render

from .auth import register_view, login_view, logout_view
from .receipts import receipt_upload_view, receipt_list_view
from .review import pending_receipts_view, receipt_detail_view, all_receipts_view
from .dashboard import dashboard_view, tenant_dashboard, admin_dashboard

__all__ = [
    'register_view', 'login_view', 'logout_view', 'dashboard_view',
    'receipt_upload_view', 'receipt_list_view',
    'pending_receipts_view', 'receipt_detail_view', 'all_receipts_view',
    'tenant_dashboard', 'admin_dashboard',
]
