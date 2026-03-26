"""Receipt-related models for budget app."""
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """Expense/Income category."""
    
    TYPE_CHOICES = [
        ('expense', 'Gasto'),
        ('income', 'Ingreso'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    name_es = models.CharField('Nombre en espanol', max_length=50)
    category_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['category_type', 'name']
    
    def __str__(self):
        return f'{self.name_es}'


class Receipt(models.Model):
    """Uploaded receipt record."""
    
    STATUS_CHOICES = [
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    RECEIPT_TYPE_CHOICES = [
        ('income', 'Ingreso'),
        ('expense', 'Gasto'),
    ]
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_receipts'
    )
    original_file_url = models.URLField(max_length=500)
    file_name = models.CharField(max_length=255)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    receipt_type = models.CharField(
        max_length=10,
        choices=RECEIPT_TYPE_CHOICES,
        default='expense'
    )
    
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

    date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    counterparty = models.CharField(max_length=200, blank=True, help_text="Vendor for expenses, payer for income")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='transactions'
    )
    description = models.TextField(blank=True)
    modified_by_user = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'receipts'
        verbose_name = 'Receipt'
        verbose_name_plural = 'Receipts'
        ordering = ['-upload_timestamp']
        indexes = [
            models.Index(fields=['status', 'upload_timestamp']),
            models.Index(fields=['uploaded_by', 'status']),
            models.Index(fields=['status', 'receipt_type', 'date']),
            models.Index(fields=['status', 'receipt_type', 'uploaded_by']),
            models.Index(fields=['category', 'status']),
        ]
    
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