from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    """Custom admin interface for User model"""
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'registration_step', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('bio', 'avatar', 'dark_mode', 'registration_step')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile', {'fields': ('bio', 'avatar', 'dark_mode', 'registration_step')}),
    )

admin.site.register(User, CustomUserAdmin) 