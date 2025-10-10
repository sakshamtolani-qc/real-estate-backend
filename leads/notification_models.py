from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Model for storing user notifications"""
    
    NOTIFICATION_TYPES = [
        ('customer_signup', 'Customer Signup'),
        ('call_scheduled', 'Call Scheduled'),
        ('property_added', 'Property Added'),
        ('lead_assigned', 'Lead Assigned'),
        ('lead_updated', 'Lead Updated'),
        ('visit_scheduled', 'Visit Scheduled'),
    ]
    
    # Basic info
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Status
    is_read = models.BooleanField(default=False)
    
    # Related data (stored as JSON-like text for flexibility)
    related_data = models.JSONField(null=True, blank=True, default=dict)
    
    # Action URL (optional)
    action_url = models.CharField(max_length=500, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        app_label = 'leads'
    
    def __str__(self):
        return f"{self.title} - {self.recipient.email}"
