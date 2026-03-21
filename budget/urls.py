"""URL configuration for budget app."""
from django.urls import path
from budget.views import register_view, login_view, logout_view, dashboard_view

app_name = 'budget'

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
