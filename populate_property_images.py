#!/usr/bin/env python
import os
import sys
import django
import shutil
from pathlib import Path

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from properties.models import Property, PropertyImage
from django.core.files import File

# Paths
FRONTEND_PUBLIC = Path(r"C:\Users\aptod\OneDrive\Desktop\real-Estate\real-estate-frontend\public")
BACKEND_MEDIA = Path(r"C:\Users\aptod\OneDrive\Desktop\real-Estate\real-estate-backend\media\properties")

# Create media/properties directory if it doesn't exist
BACKEND_MEDIA.mkdir(parents=True, exist_ok=True)

print("\n" + "="*60)
print("Property Images Population Script")
print("="*60)

# Available property images in frontend public folder
property_images = {
    'P1.png': ['P1a.png', 'P1b.png', 'P1c.png', 'P1d.png', 'P1e.png'],
    'P2.png': [],
    'P3.png': []
}

# Get all properties
properties = Property.objects.all()
print(f"\nTotal Properties: {properties.count()}")

if properties.count() == 0:
    print("No properties found in database!")
    sys.exit(1)

# Track statistics
images_created = 0
properties_updated = 0

# Assign images to properties in a round-robin fashion
for index, property_obj in enumerate(properties):
    # Delete existing images for this property
    existing_images = property_obj.images.all()
    if existing_images.exists():
        print(f"  Removing {existing_images.count()} existing images for: {property_obj.title}")
        existing_images.delete()
    
    # Determine which image set to use (cycle through P1, P2, P3)
    image_set_index = (index % 3) + 1
    main_image = f"P{image_set_index}.png"
    
    # Get additional images for this set
    additional_images = property_images.get(main_image, [])
    
    # List of all images to add (main + additional)
    all_images = [main_image] + additional_images
    
    print(f"\n  Property: {property_obj.title}")
    print(f"    Assigning {len(all_images)} image(s)")
    
    # Copy and create PropertyImage records
    for img_index, img_name in enumerate(all_images):
        source_path = FRONTEND_PUBLIC / img_name
        
        if not source_path.exists():
            print(f"      ⚠ Image not found: {img_name}")
            continue
        
        # Copy image to media folder with a unique name
        dest_filename = f"property_{property_obj.id}_{img_index}_{img_name}"
        dest_path = BACKEND_MEDIA / dest_filename
        
        try:
            # Copy the file
            shutil.copy2(source_path, dest_path)
            
            # Create PropertyImage record
            with open(dest_path, 'rb') as f:
                property_image = PropertyImage.objects.create(
                    property=property_obj,
                    title=f"{property_obj.title} - Image {img_index + 1}",
                    is_primary=(img_index == 0),  # First image is primary
                    order=img_index
                )
                # Update the image field to point to the copied file
                property_image.image.name = f"properties/{dest_filename}"
                property_image.save()
            
            print(f"      ✓ Added: {img_name} {'(Primary)' if img_index == 0 else ''}")
            images_created += 1
            
        except Exception as e:
            print(f"      ✗ Error with {img_name}: {e}")
    
    properties_updated += 1

print("\n" + "="*60)
print(f"✅ Population Complete!")
print(f"   Properties Updated: {properties_updated}")
print(f"   Images Created: {images_created}")
print("="*60 + "\n")

# Verify
print("Verification:")
for prop in Property.objects.all():
    img_count = prop.images.count()
    primary = prop.images.filter(is_primary=True).first()
    status = "✓" if img_count > 0 else "⚠"
    print(f"  {status} {prop.title}: {img_count} image(s)" + 
          (f" (Primary: {primary.image.name})" if primary else ""))
