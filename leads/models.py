from django.db import models
from django.contrib.auth.models import User
from accounts.models import Employee
from properties.models import Property


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