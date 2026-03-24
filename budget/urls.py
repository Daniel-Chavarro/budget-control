"""URL configuration for budget app."""
from django.urls import path
from budget.views import register_view, login_view, logout_view, dashboard_view
from budget.views import receipt_upload_view, receipt_list_view
from budget.views import pending_receipts_view, receipt_detail_view, all_receipts_view
from budget.views.management import (
    user_management_view, user_create_view, user_delete_view,
    category_list_view, category_create_view, category_edit_view, category_delete_view
)
from budget.views.reports import expense_report_view

app_name = 'budget'

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('users/', user_management_view, name='user_management'),
    path('users/create/', user_create_view, name='user_create'),
    path('users/<int:pk>/delete/', user_delete_view, name='user_delete'),
    path('receipts/', receipt_list_view, name='receipt_list'),
    path('receipts/upload/', receipt_upload_view, name='receipt_upload'),
    path('review/pending/', pending_receipts_view, name='pending_receipts'),
    path('review/<int:pk>/', receipt_detail_view, name='receipt_detail'),
    path('review/all/', all_receipts_view, name='all_receipts'),
    path('reports/expenses/', expense_report_view, name='expense_report'),
    path('categories/', category_list_view, name='category_list'),
    path('categories/create/', category_create_view, name='category_create'),
    path('categories/<int:pk>/edit/', category_edit_view, name='category_edit'),
    path('categories/<int:pk>/delete/', category_delete_view, name='category_delete'),
]
