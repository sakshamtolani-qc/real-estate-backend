#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from properties.models import Property, PropertyImage

print("\n" + "="*60)
print("Property Images Check")
print("="*60)

properties = Property.objects.all()
print(f"\nTotal Properties: {properties.count()}")

properties_without_images = 0
for prop in properties:
    images_count = prop.images.count()
    if images_count == 0:
        properties_without_images += 1
        print(f"  ⚠ {prop.title}: No images")
    else:
        print(f"  ✓ {prop.title}: {images_count} image(s)")

print(f"\nProperties without images: {properties_without_images}")
print(f"Total PropertyImage records: {PropertyImage.objects.count()}")
print("="*60 + "\n")
