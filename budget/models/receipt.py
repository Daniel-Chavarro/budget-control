"""Receipt-related models for budget app."""
from django.db import models
from django.contrib.auth.models import User


class Receipt(models.Model):
    """Uploaded receipt record."""
    
    STATUS_CHOICES = [
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_receipts'
    )
    original_file_url = models.URLField(max_length=500)
    file_name = models.CharField(max_length=255)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_review'
    )
    
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_receipts'
    )
    review_timestamp = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'receipts'
        verbose_name = 'Receipt'
        verbose_name_plural = 'Receipts'
        ordering = ['-upload_timestamp']
    
    def __str__(self):
        return f'Receipt {self.file_name} by {self.uploaded_by.username}'
    
    @property
    def is_pending(self):
        """Check if receipt is pending review."""
        return self.status == 'pending_review'
    
    @property
    def is_approved(self):
        """Check if receipt is approved."""
        return self.status == 'approved'
    
    @property
    def is_rejected(self):
        """Check if receipt is rejected."""
        return self.status == 'rejected'


class ExpenseData(models.Model):
    """Extracted/edited expense data from receipt."""
    
    CATEGORY_CHOICES = [
        ('maintenance', 'Maintenance'),
        ('utilities', 'Utilities'),
        ('cleaning', 'Cleaning'),
        ('security', 'Security'),
        ('repairs', 'Repairs'),
        ('other', 'Other'),
    ]
    
    receipt = models.OneToOneField(
        Receipt,
        on_delete=models.CASCADE,
        related_name='expense_data'
    )
    
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    vendor = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    modified_by_user = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'expense_data'
        verbose_name = 'Expense Data'
        verbose_name_plural = 'Expense Data'
    
    def __str__(self):
        return f'{self.vendor} - ${self.amount} ({self.date})'
