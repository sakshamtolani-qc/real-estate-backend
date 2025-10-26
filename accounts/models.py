from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    is_employee = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    
    # Profile fields
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    about = models.TextField(blank=True, help_text="About/Bio section")
    
    @property
    def profile_photo_url(self):
        """Get absolute URL for profile photo"""
        if self.profile_photo:
            return self.profile_photo.url
        return None

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_joined = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('InActive', 'InActive')], default='Active')
    # Add more fields as needed

    def __str__(self):
        return self.user.get_full_name() or self.user.username
