"""Test suite for receipt models."""
from django.test import TestCase
from django.contrib.auth.models import User
from budget.models import Receipt, Category
from decimal import Decimal
from datetime import date


class TestReceiptModel(TestCase):
    """Test Receipt model."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='tenant', password='pass')
        self.category = Category.objects.create(
            name='Servicios',
            category_type='gasto'
        )
    
    def test_create_receipt(self):
        """Test creating receipt."""
        receipt = Receipt.objects.create(
            uploaded_by=self.user,
            original_file_url='https://example.com/file.jpg',
            file_name='receipt_001.jpg',
            status='pendiente'
        )
        assert receipt.uploaded_by == self.user
        assert receipt.status == 'pendiente'
        assert receipt.is_pending
        assert str(receipt) == f'Receipt receipt_001.jpg by tenant'
    
    def test_create_receipt_with_expense_data(self):
        """Test creating receipt with expense data."""
        receipt = Receipt.objects.create(
            uploaded_by=self.user,
            original_file_url='https://example.com/file.jpg',
            file_name='receipt.jpg',
            date=date.today(),
            amount=Decimal('99.99'),
            counterparty='Test Vendor',
            category=self.category,
            description='Electric bill',
            modified_by_user=True
        )
        assert receipt.amount == Decimal('99.99')
        assert receipt.counterparty == 'Test Vendor'
        assert receipt.modified_by_user
