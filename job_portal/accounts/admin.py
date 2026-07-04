from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, OTPDevice, RecoveryCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'role', 'is_email_verified', 'two_factor_enabled', 'is_active']
    list_filter = ['role', 'is_active', 'is_email_verified', 'two_factor_enabled']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Security', {'fields': ('role', 'is_email_verified', 'two_factor_enabled')}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'experience_years', 'company_name']
    search_fields = ['user__email', 'location', 'company_name']


@admin.register(OTPDevice)
class OTPDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified', 'created_at']


@admin.register(RecoveryCode)
class RecoveryCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'is_used', 'created_at']
