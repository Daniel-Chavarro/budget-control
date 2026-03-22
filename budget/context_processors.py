"""Context processors for budget app."""
from budget.models import Receipt


def pending_receipts_count(request):
    """Add pending receipts count to template context."""
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        if request.user.userprofile.is_admin:
            count = Receipt.objects.filter(status='pending_review').count()
            return {'pending_count': count}
    return {'pending_count': 0}
