from django.db import models
from django.contrib.auth.models import User
import uuid


class PropertyType(models.Model):
    """Property types like apartment, house, villa, etc."""
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class Property(models.Model):
    """Main property model"""
    LISTING_TYPE_CHOICES = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    ]
    
    FURNISHED_STATUS_CHOICES = [
        ('unfurnished', 'Unfurnished'),
        ('semi_furnished', 'Semi Furnished'),
        ('fully_furnished', 'Fully Furnished'),
    ]
    
    # Basic info
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    property_type = models.ForeignKey(PropertyType, on_delete=models.PROTECT)
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Location
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=200)  # Display location
    
    # Property details
    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)
    square_feet = models.IntegerField(default=0)
    area = models.CharField(max_length=50)  # Display area like "450 sqft"
    parking_spaces = models.IntegerField(default=0)
    furnished_status = models.CharField(max_length=20, choices=FURNISHED_STATUS_CHOICES, blank=True)
    
    # Pricing
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rent_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.CharField(max_length=100)  # Display price
    
    # Features
    has_pool = models.BooleanField(default=False)
    has_garden = models.BooleanField(default=False)
    
    # Listing info
    description = models.TextField()
    featured = models.BooleanField(default=False)
    date_listed = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0)
    
    # SEO
    slug = models.SlugField(max_length=250, blank=True)
    
    class Meta:
        ordering = ['-date_listed']
        verbose_name_plural = 'Properties'
    
    def __str__(self):
        return self.title
    
    @property
    def image(self):
        """Get primary image URL - handles both Cloudinary and local images"""
        first_image = self.images.filter(is_primary=True).first()
        if first_image:
            # For Cloudinary URLs, just return as string
            image_str = str(first_image.image)
            if image_str.startswith('http'):
                return image_str
            # For local files, get the URL
            return first_image.image.url
        
        any_image = self.images.first()
        if any_image:
            # For Cloudinary URLs, just return as string
            image_str = str(any_image.image)
            if image_str.startswith('http'):
                return image_str
            # For local files, get the URL
            return any_image.image.url
        
        return None  # Return None so frontend can use its own fallback images
    
    @property
    def type(self):
        """Get property type name for frontend compatibility"""
        return self.property_type.name


class PropertyImage(models.Model):
    """Images for properties"""
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='properties/', max_length=500)  # Extended for Cloudinary URLs
    title = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.property.title} - Image {self.order}"


class PropertyFeature(models.Model):
    """Additional features/amenities for properties"""
    property = models.ForeignKey(Property, related_name='features', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
