"""
Test suite for budget app models.
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from budget.models import UserProfile


class TestUserProfile(TestCase):
    """Test UserProfile model."""
    
    def test_user_profile_auto_created(self):
        """Test user profile is auto-created with default role."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Profile should be auto-created by signal
        assert hasattr(user, 'userprofile')
        profile = user.userprofile
        
        assert profile.user == user
        assert profile.role == 'inquilino'  # Default role
        assert str(profile) == 'testuser (inquilino)'
    
    def test_user_profile_update(self):
        """Test updating a user profile."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Update the auto-created profile
        profile = user.userprofile
        profile.role = 'admin'
        profile.phone = '1234567890'
        profile.save()
        
        # Refresh from database
        profile.refresh_from_db()
        
        assert profile.role == 'admin'
        assert profile.phone == '1234567890'
    
    def test_user_profile_role_choices(self):
        """Test role field accepts valid choices."""
        for role in ['admin', 'inquilino', 'sin_vinculo']:
            user = User.objects.create_user(
                username=f'test_{role}',
                password='pass'
            )
            profile = user.userprofile
            profile.role = role
            profile.full_clean()  # Should not raise validation error
    
    def test_user_profile_properties(self):
        """Test role property methods."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        profile = user.userprofile
        
        # Test is_tenant
        profile.role = 'inquilino'
        assert profile.is_tenant
        assert not profile.is_admin
        assert not profile.is_unlinked_user
        
        # Test is_admin
        profile.role = 'admin'
        assert profile.is_admin
        assert not profile.is_tenant
        
        # Test is_unlinked_user
        profile.role = 'sin_vinculo'
        assert profile.is_unlinked_user
        assert not profile.is_tenant


class TestProjectSetup(TestCase):
    """Verify project setup is working."""
    
    def test_django_environment(self):
        """Test that Django test environment is configured."""
        assert True


def test_userprofile_admin_display():
    """Test UserProfile displays correctly in admin."""
    from django.contrib import admin
    from budget.admin import UserProfileAdmin
    from budget.models import UserProfile
    
    # Check UserProfile is registered
    assert UserProfile in admin.site._registry
