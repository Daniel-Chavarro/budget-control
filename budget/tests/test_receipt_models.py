"""Test suite for receipt models."""
from django.test import TestCase
from django.contrib.auth.models import User
from budget.models import Receipt, ExpenseData
from decimal import Decimal
from datetime import date


class TestReceiptModel(TestCase):
    """Test Receipt model."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='tenant', password='pass')
    
    def test_create_receipt(self):
        """Test creating receipt."""
        receipt = Receipt.objects.create(
            uploaded_by=self.user,
            original_file_url='https://example.com/file.jpg',
            file_name='receipt_001.jpg',
            status='pending_review'
        )
        assert receipt.uploaded_by == self.user
        assert receipt.status == 'pending_review'
        assert receipt.is_pending
        assert str(receipt) == f'Receipt receipt_001.jpg by tenant'


class TestExpenseDataModel(TestCase):
    """Test ExpenseData model."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='tenant', password='pass')
        self.receipt = Receipt.objects.create(
            uploaded_by=self.user,
            original_file_url='https://example.com/file.jpg',
            file_name='receipt.jpg'
        )
    
    def test_create_expense_data(self):
        """Test creating expense data."""
        expense = ExpenseData.objects.create(
            receipt=self.receipt,
            date=date.today(),
            amount=Decimal('99.99'),
            vendor='Test Vendor',
            category='utilities',
            description='Electric bill'
        )
        assert expense.amount == Decimal('99.99')
        assert expense.vendor == 'Test Vendor'
        assert not expense.modified_by_user
