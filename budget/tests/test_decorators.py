"""Test suite for budget app decorators."""
import pytest
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.http import HttpResponse
from budget.decorators import admin_required, tenant_or_admin_required
from budget.models import UserProfile


class TestPermissionDecorators(TestCase):
    """Test role-based permission decorators."""
    
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin', password='pass'
        )
        self.admin_user.userprofile.role = 'admin'
        self.admin_user.userprofile.save()
        
        self.tenant_user = User.objects.create_user(
            username='tenant', password='pass'
        )
        self.tenant_user.userprofile.role = 'inquilino'
        self.tenant_user.userprofile.save()
        
        self.unlinked_user = User.objects.create_user(
            username='unlinked', password='pass'
        )
        self.unlinked_user.userprofile.role = 'sin_vinculo'
        self.unlinked_user.userprofile.save()
    
    def test_admin_required_allows_admin(self):
        """Test admin_required allows admin users."""
        @admin_required
        def test_view(request):
            return HttpResponse('Success')
        
        request = self.factory.get('/test/')
        request.user = self.admin_user
        response = test_view(request)
        
        assert response.status_code == 200
        assert b'Success' in response.content
    
    def test_admin_required_blocks_tenant(self):
        """Test admin_required blocks tenant users."""
        @admin_required
        def test_view(request):
            return HttpResponse('Success')
        
        request = self.factory.get('/test/')
        request.user = self.tenant_user
        response = test_view(request)
        
        # Should redirect or return 403
        assert response.status_code in [302, 403]
    
    def test_tenant_or_admin_required_allows_both(self):
        """Test tenant_or_admin_required allows both roles."""
        @tenant_or_admin_required
        def test_view(request):
            return HttpResponse('Success')
        
        for user in [self.admin_user, self.tenant_user]:
            request = self.factory.get('/test/')
            request.user = user
            response = test_view(request)
            assert response.status_code == 200
    
    def test_tenant_or_admin_required_blocks_unlinked(self):
        """Test tenant_or_admin_required blocks unlinked users."""
        @tenant_or_admin_required
        def test_view(request):
            return HttpResponse('Success')
        
        request = self.factory.get('/test/')
        request.user = self.unlinked_user
        response = test_view(request)
        
        assert response.status_code in [302, 403]
