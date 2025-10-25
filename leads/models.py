from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from accounts.models import Employee
from properties.models import Property
from .settings_model import CompanySettings


class LeadSource(models.Model):
    """Sources where leads come from"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "leads"
    
    def __str__(self):
        return self.name


class LeadNote(models.Model):
    """Individual notes for leads"""
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='lead_notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        app_label = "leads"
    
    def __str__(self):
        return f"Note for {self.lead.full_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Lead(models.Model):
    """Customer leads"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]
    
    # Basic info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Lead details
    source = models.ForeignKey(LeadSource, on_delete=models.PROTECT, related_name='leads')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_leads')
    
    # Property interest
    interested_in = models.ManyToManyField(Property, blank=True, related_name='interested_leads')
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Follow-up
    follow_up_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        app_label = "leads"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.status}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Deal(models.Model):
    """Closed deals/transactions"""
    DEAL_TYPE_CHOICES = [
        ('sale', 'Sale'),
        ('rent', 'Rental'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Relationships
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='deals')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='deals')
    closed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='closed_deals')
    
    # Deal details
    deal_type = models.CharField(max_length=10, choices=DEAL_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Financial
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Dates
    offer_date = models.DateField()
    closing_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-closing_date', '-created_at']
        app_label = "leads"
    
    def __str__(self):
        return f"Deal: {self.property.title} - {self.lead.full_name} ({self.status})"


class ScheduledVisit(models.Model):
    """Model for scheduled property visits"""
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Relationships
    agent = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='scheduled_visits')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True, related_name='visits')
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, null=True, blank=True, related_name='visits')
    
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
    
    # Related data (stored as JSON for flexibility)
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
