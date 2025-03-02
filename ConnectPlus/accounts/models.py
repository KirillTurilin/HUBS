from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class User(AbstractUser):
    """Custom user model with additional profile fields"""
    email = models.EmailField(_('email address'), unique=True)
    
    # Profile information
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    bio = models.TextField(_('biography'), max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    dark_mode = models.BooleanField(default=False)
    
    # Registration completion tracking
    registration_step = models.IntegerField(default=1)  # 1: Basic info, 2: Profile details, 3: Avatar, 4: Complete
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    def __str__(self):
        return self.username
    
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.username})
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def registration_complete(self):
        return self.registration_step >= 4 