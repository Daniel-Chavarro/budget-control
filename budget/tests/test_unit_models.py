"""Test suite for unit models."""
from django.test import TestCase
from django.contrib.auth.models import User
from budget.models import Unit, UserUnit
from decimal import Decimal
from datetime import date, timedelta


class TestUnitModel(TestCase):
    """Test Unit model."""
    
    def test_create_apartment_unit(self):
        """Test creating apartment unit."""
        unit = Unit.objects.create(
            type='apartment',
            identifier='A-101',
            status='active',
            monthly_fee=Decimal('150.00')
        )
        assert unit.identifier == 'A-101'
        assert unit.type == 'apartment'
        assert unit.is_apartment
        assert not unit.is_parking
        assert str(unit) == 'Apartment A-101'
    
    def test_create_parking_unit(self):
        """Test creating parking unit."""
        unit = Unit.objects.create(
            type='public_parking',
            identifier='P-05',
            status='active',
            monthly_fee=Decimal('50.00')
        )
        assert unit.is_parking
        assert str(unit) == 'Parking P-05'


class TestUserUnitModel(TestCase):
    """Test UserUnit relationship model."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='tenant', password='pass')
        self.unit = Unit.objects.create(
            type='apartment',
            identifier='A-201',
            status='active'
        )
    
    def test_create_user_unit_relationship(self):
        """Test creating user-unit relationship."""
        user_unit = UserUnit.objects.create(
            user=self.user,
            unit=self.unit,
            role_in_unit='owner',
            start_date=date.today()
        )
        assert user_unit.user == self.user
        assert user_unit.unit == self.unit
        assert user_unit.is_active
        assert str(user_unit) == f'tenant - Apartment A-201 (owner)'
    
    def test_user_unit_active_status(self):
        """Test is_active property."""
        # Active: no end_date
        active = UserUnit.objects.create(
            user=self.user,
            unit=self.unit,
            role_in_unit='tenant',
            start_date=date.today()
        )
        assert active.is_active
        
        # Inactive: end_date in past
        inactive = UserUnit.objects.create(
            user=self.user,
            unit=self.unit,
            role_in_unit='tenant',
            start_date=date.today() - timedelta(days=60),
            end_date=date.today() - timedelta(days=1)
        )
        assert not inactive.is_active
