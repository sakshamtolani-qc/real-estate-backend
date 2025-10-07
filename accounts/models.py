from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    is_employee = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    # Add more fields as needed

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_joined = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('InActive', 'InActive')], default='Active')
    # Add more fields as needed

    def __str__(self):
        return self.user.get_full_name() or self.user.username
