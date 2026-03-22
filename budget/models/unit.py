"""Unit-related models for budget app."""
from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Unit(models.Model):
    """Apartment or parking slot unit."""
    
    TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('public_parking', 'Public Parking'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    identifier = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Monthly fee if applicable'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'units'
        verbose_name = 'Unit'
        verbose_name_plural = 'Units'
        ordering = ['identifier']
    
    def __str__(self):
        type_label = 'Apartment' if self.type == 'apartment' else 'Parking'
        return f'{type_label} {self.identifier}'
    
    @property
    def is_apartment(self):
        """Check if unit is apartment."""
        return self.type == 'apartment'
    
    @property
    def is_parking(self):
        """Check if unit is parking."""
        return self.type == 'public_parking'


class UserUnit(models.Model):
    """Many-to-many relationship between users and units."""
    
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('tenant', 'Tenant'),
        ('authorized_user', 'Authorized User'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_units')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='unit_users')
    role_in_unit = models.CharField(max_length=20, choices=ROLE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_units'
        verbose_name = 'User Unit Relationship'
        verbose_name_plural = 'User Unit Relationships'
        unique_together = [['user', 'unit', 'start_date']]
    
    def __str__(self):
        return f'{self.user.username} - {self.unit} ({self.role_in_unit})'
    
    @property
    def is_active(self):
        """Check if relationship is currently active."""
        if self.end_date is None:
            return True
        return self.end_date >= date.today()
