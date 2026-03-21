"""
Test suite for budget app models.
"""
import pytest
from django.test import TestCase


class TestProjectSetup(TestCase):
    """Verify project setup is working."""
    
    def test_django_environment(self):
        """Test that Django test environment is configured."""
        assert True
