"""Admin configuration for accounts app"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, RestaurantAccess, NotificationPreference


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""

    list_display = ['email', 'first_name', 'last_name', 'role', 'organization', 'is_active']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'profile_image')}),
        ('Role & Organization', {'fields': ('role', 'organization')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'organization'),
        }),
    )


@admin.register(RestaurantAccess)
class RestaurantAccessAdmin(admin.ModelAdmin):
    """Admin for RestaurantAccess model"""

    list_display = ['user', 'restaurant', 'access_level', 'granted_at']
    list_filter = ['access_level', 'granted_at']
    search_fields = ['user__email', 'restaurant__name']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin for NotificationPreference model"""

    list_display = ['user', 'email_alerts', 'sms_alerts', 'push_alerts']
    list_filter = ['email_alerts', 'sms_alerts', 'push_alerts']
