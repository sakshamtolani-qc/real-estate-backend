from django.db import models
from accounts.models import User
from properties.models import Property
from leads.models import Lead


class ScheduledVisit(models.Model):
    """Model for scheduled property visits"""
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Relationships
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_visits')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True, related_name='visits')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True, related_name='visits')
    
    # Visit details
    visit_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=300)
    
    # Participants (stored as comma-separated emails or names)
    participants = models.TextField(blank=True, help_text="Comma-separated list of participant emails")
    
    # Recurring settings
    is_recurring = models.BooleanField(default=False)
    recurring_days = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Comma-separated days: Mon,Tue,Wed,Thu,Fri,Sat,Sun"
    )
    
    # Status
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['visit_date', 'start_time']
        app_label = 'leads'
    
    def __str__(self):
        return f"{self.title} - {self.visit_date} at {self.start_time}"
