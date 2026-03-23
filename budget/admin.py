"""Django admin configuration for budget app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from budget.models import Unit, UserProfile, UserUnit, Receipt


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['role', 'phone', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


class UserAdmin(BaseUserAdmin):
    """Extended User admin with UserProfile inline."""
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'get_role', 'is_active', 'date_joined']
    list_filter = ['is_active', 'userprofile__role', 'date_joined']
    
    def get_role(self, obj):
        """Display user role."""
        return obj.userprofile.role if hasattr(obj, 'userprofile') else '-'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'userprofile__role'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile."""
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """Admin interface for Unit."""
    list_display = ['identifier', 'type', 'status', 'monthly_fee', 'created_at']
    list_filter = ['type', 'status', 'created_at']
    search_fields = ['identifier']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserUnit)
class UserUnitAdmin(admin.ModelAdmin):
    """Admin interface for UserUnit."""
    list_display = ['user', 'unit', 'role_in_unit', 'start_date', 'end_date', 'is_active']
    list_filter = ['role_in_unit', 'start_date']
    search_fields = ['user__username', 'unit__identifier']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    """Admin for receipts."""
    list_display = ['file_name', 'uploaded_by', 'receipt_type', 'status', 'amount', 'counterparty', 'upload_timestamp']
    list_filter = ['status', 'receipt_type', 'upload_timestamp']
    search_fields = ['file_name', 'uploaded_by__username', 'counterparty']
    readonly_fields = ['upload_timestamp', 'review_timestamp']