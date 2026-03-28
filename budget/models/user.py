"""User-related models for budget app."""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with role and contact info."""
    
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('inquilino', 'Inquilino'),
        ('sin_vinculo', 'Sin Vínculo'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='userprofile'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='inquilino'
    )
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"
    
    @property
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'
    
    @property
    def is_tenant(self):
        """Check if user has tenant role."""
        return self.role == 'inquilino'
    
    @property
    def is_unlinked_user(self):
        """Check if user is unlinked user."""
        return self.role == 'sin_vinculo'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile when User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved."""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
