from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from properties.models import PropertyImage
import cloudinary.uploader
import os
import shutil
from pathlib import Path
from django.conf import settings


class Command(BaseCommand):
    help = 'Migrate all local property images to Cloudinary'

    def handle(self, *args, **options):
        """
        Migrate all PropertyImage instances from local storage to Cloudinary.
        Updates the image field with the Cloudinary URL.
        """
        self.stdout.write(self.style.SUCCESS('Starting image migration to Cloudinary...'))

        # Get all PropertyImage instances
        property_images = PropertyImage.objects.all()
        total = property_images.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('No images found to migrate.'))
            return

        self.stdout.write(f'Found {total} images to migrate.')

        migrated = 0
        failed = 0
        skipped = 0

        for idx, prop_image in enumerate(property_images, 1):
            try:
                # Skip if already using Cloudinary (URL instead of file)
                image_path = str(prop_image.image)
                
                # Check if it's already a Cloudinary URL
                if 'cloudinary' in image_path or 'res.cloudinary.com' in image_path:
                    self.stdout.write(
                        self.style.WARNING(f'[{idx}/{total}] Skipping {prop_image.id} - Already on Cloudinary')
                    )
                    skipped += 1
                    continue

                # Check if the image file exists
                if not prop_image.image:
                    self.stdout.write(
                        self.style.WARNING(f'[{idx}/{total}] Skipping {prop_image.id} - No image file')
                    )
                    skipped += 1
                    continue

                # Try to get the file path from local media directory
                media_root = settings.MEDIA_ROOT
                image_name = prop_image.image.name
                local_file_path = os.path.join(media_root, image_name)
                
                if not os.path.exists(local_file_path):
                    # Try alternative path
                    alt_path = os.path.join(media_root, str(image_name))
                    if not os.path.exists(alt_path):
                        self.stdout.write(
                            self.style.WARNING(f'[{idx}/{total}] Skipping {prop_image.id} - File not found: {local_file_path}')
                        )
                        skipped += 1
                        continue
                    local_file_path = alt_path

                # Upload to Cloudinary
                filename = os.path.basename(local_file_path)
                public_id = f"real-estate/property_{prop_image.property_id}_{prop_image.id}_{filename.split('.')[0]}"
                
                result = cloudinary.uploader.upload(
                    local_file_path,
                    public_id=public_id,
                    folder='real-estate/properties',
                    overwrite=True,
                    resource_type='image'
                )

                if result.get('secure_url'):
                    # Update the PropertyImage with the Cloudinary URL
                    prop_image.image = result['secure_url']
                    prop_image.save(update_fields=['image'])

                    self.stdout.write(
                        self.style.SUCCESS(f'[{idx}/{total}] ✓ Migrated {prop_image.id}')
                    )
                    migrated += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f'[{idx}/{total}] ✗ Upload failed for {prop_image.id} - No secure_url in response')
                    )
                    failed += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'[{idx}/{total}] ✗ Error migrating {prop_image.id}: {str(e)}')
                )
                failed += 1

        # Print summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'Migration Complete!'))
        self.stdout.write(f'Total: {total}')
        self.stdout.write(self.style.SUCCESS(f'Successfully migrated: {migrated}'))
        self.stdout.write(self.style.WARNING(f'Skipped: {skipped}'))
        self.stdout.write(self.style.ERROR(f'Failed: {failed}'))
        self.stdout.write('='*60)
