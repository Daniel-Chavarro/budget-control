"""URL configuration for budget app."""
from django.urls import path
from budget.views import register_view, login_view, logout_view, dashboard_view
from budget.views.management import (
    unit_list_view, unit_create_view, unit_edit_view, unit_delete_view
)

app_name = 'budget'

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('units/', unit_list_view, name='unit_list'),
    path('units/create/', unit_create_view, name='unit_create'),
    path('units/<int:pk>/edit/', unit_edit_view, name='unit_edit'),
    path('units/<int:pk>/delete/', unit_delete_view, name='unit_delete'),
]
