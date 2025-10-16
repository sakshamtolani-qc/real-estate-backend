from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Employee

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with additional fields"""
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'is_employee', 'is_client')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_employee', 'is_client', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    list_filter = ('is_employee', 'is_client', 'is_staff', 'is_superuser', 'date_joined')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin for Employee model"""
    list_display = ('get_full_name', 'get_email', 'status', 'date_joined')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'user__username')
    list_filter = ('status', 'date_joined')
    readonly_fields = ('date_joined',)
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Full Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
