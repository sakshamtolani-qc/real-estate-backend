from django.db import models


class CompanySettings(models.Model):
    """Model to store company-wide settings and configuration"""
    
    # Singleton pattern - only one settings record should exist
    company_name = models.CharField(max_length=200, default='Real Estate CRM')
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=500, blank=True)
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Company Details
    about = models.TextField(blank=True)
    policies = models.TextField(blank=True)
    
    # Logo/Branding (stored in Cloudinary)
    logo_url = models.CharField(max_length=500, blank=True, help_text="Cloudinary URL for company logo")
    logo_public_id = models.CharField(max_length=500, blank=True, help_text="Cloudinary public_id for logo management")
    
    # Additional contact options
    additional_emails = models.JSONField(default=list, blank=True)  # List of additional emails
    additional_phones = models.JSONField(default=list, blank=True)  # List of additional phones
    
    # Social Media Links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Business Hours
    business_hours = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Company Settings'
        app_label = 'leads'
    
    def __str__(self):
        return f"{self.company_name} Settings"
    
    def save(self, *args, **kwargs):
        """Ensure only one settings record exists"""
        if not self.pk and CompanySettings.objects.exists():
            # Update existing record instead of creating a new one
            obj = CompanySettings.objects.first()
            self.pk = obj.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the single settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
