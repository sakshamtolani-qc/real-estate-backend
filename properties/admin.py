from django.contrib import admin
from .models import Property, PropertyType, PropertyImage, PropertyFeature

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
	list_display = ('title', 'property_type', 'listing_type', 'status', 'city', 'featured', 'date_listed')
	search_fields = ('title', 'city', 'state', 'address')
	list_filter = ('property_type', 'listing_type', 'status', 'featured', 'city')

@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
	list_display = ('name', 'description')

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
	list_display = ('property', 'title', 'is_primary', 'order', 'created_at')
	list_filter = ('is_primary',)

@admin.register(PropertyFeature)
class PropertyFeatureAdmin(admin.ModelAdmin):
	list_display = ('property', 'name')
