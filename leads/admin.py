from django.contrib import admin
from .models import Lead, LeadSource, LeadNote, Deal, ScheduledVisit, Notification
from .settings_model import CompanySettings

@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    """Admin for LeadSource model"""
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)

class LeadNoteInline(admin.TabularInline):
    """Inline admin for LeadNote"""
    model = LeadNote
    extra = 1
    readonly_fields = ('created_at', 'created_by')
    fields = ('note', 'created_by', 'created_at')

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """Admin for Lead model"""
    list_display = ('full_name', 'email', 'phone', 'status', 'assigned_to', 'source', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_filter = ('status', 'source', 'assigned_to', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    inlines = [LeadNoteInline]
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Lead Details', {
            'fields': ('source', 'status', 'assigned_to', 'created_by')
        }),
        ('Property Interest', {
            'fields': ('interested_in', 'budget_min', 'budget_max')
        }),
        ('Notes & Follow-up', {
            'fields': ('notes', 'follow_up_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(LeadNote)
class LeadNoteAdmin(admin.ModelAdmin):
    """Admin for LeadNote model"""
    list_display = ('lead', 'created_by', 'created_at')
    search_fields = ('lead__first_name', 'lead__last_name', 'note')
    list_filter = ('created_at', 'created_by')
    readonly_fields = ('created_at',)

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    """Admin for Deal model"""
    list_display = ('property', 'lead', 'deal_type', 'status', 'amount', 'closed_by', 'offer_date', 'closing_date')
    search_fields = ('lead__first_name', 'lead__last_name', 'property__title')
    list_filter = ('deal_type', 'status', 'closed_by', 'offer_date', 'closing_date')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Deal Information', {
            'fields': ('lead', 'property', 'closed_by', 'deal_type', 'status')
        }),
        ('Financial', {
            'fields': ('amount', 'commission')
        }),
        ('Dates', {
            'fields': ('offer_date', 'closing_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ScheduledVisit)
class ScheduledVisitAdmin(admin.ModelAdmin):
    """Admin for ScheduledVisit model"""
    list_display = ('title', 'agent', 'property', 'lead', 'visit_date', 'start_time', 'status')
    search_fields = ('title', 'agent__first_name', 'agent__last_name', 'property__title', 'lead__first_name', 'lead__last_name')
    list_filter = ('status', 'visit_date', 'is_recurring')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Visit Details', {
            'fields': ('title', 'description', 'agent', 'lead', 'property')
        }),
        ('Schedule', {
            'fields': ('visit_date', 'start_time', 'end_time', 'location')
        }),
        ('Participants & Recurring', {
            'fields': ('participants', 'is_recurring', 'recurring_days')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notification model"""
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    search_fields = ('recipient__email', 'title', 'message')
    list_filter = ('notification_type', 'is_read', 'created_at')
    readonly_fields = ('created_at', 'read_at')
    fieldsets = (
        ('Recipient & Type', {
            'fields': ('recipient', 'notification_type')
        }),
        ('Content', {
            'fields': ('title', 'message', 'action_url')
        }),
        ('Status', {
            'fields': ('is_read', 'related_data')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'read_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    """Admin for CompanySettings model"""
    list_display = ('company_name', 'phone', 'email', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Company Info', {
            'fields': ('company_name', 'country', 'city', 'address')
        }),
        ('Contact', {
            'fields': ('phone', 'email', 'additional_phones', 'additional_emails')
        }),
        ('Media (Cloudinary)', {
            'fields': ('logo_url', 'logo_public_id'),
            'description': 'Logo is stored in Cloudinary. Update logo_url with the Cloudinary URL.'
        }),
        ('Content', {
            'fields': ('about', 'policies')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url')
        }),
        ('Business Hours', {
            'fields': ('business_hours',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Only allow one instance to exist"""
        return not CompanySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of settings"""
        return False
