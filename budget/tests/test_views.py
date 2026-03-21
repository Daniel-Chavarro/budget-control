"""Test suite for budget app views."""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class TestRegistrationView(TestCase):
    """Test user registration."""
    
    def setUp(self):
        self.client = Client()
    
    def test_registration_page_loads(self):
        """Test registration page is accessible."""
        response = self.client.get(reverse('budget:register'))
        assert response.status_code == 200
        assert b'Register' in response.content
    
    def test_user_registration_success(self):
        """Test successful user registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'phone': '1234567890',
        }
        response = self.client.post(reverse('budget:register'), data)
        
        assert response.status_code == 302
        assert User.objects.filter(username='newuser').exists()
        
        user = User.objects.get(username='newuser')
        assert hasattr(user, 'userprofile')
        assert user.userprofile.phone == '1234567890'
    
    def test_registration_password_mismatch(self):
        """Test registration fails with password mismatch."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass123!',
        }
        response = self.client.post(reverse('budget:register'), data)
        
        assert response.status_code == 200
        assert not User.objects.filter(username='newuser').exists()
