import cloudinary
import cloudinary.uploader
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CloudinaryService:
    """Service to handle Cloudinary uploads for settings"""

    @staticmethod
    def upload_logo(image_file, folder='company_logos'):
        """
        Upload logo to Cloudinary and return the URL
        
        Args:
            image_file: Django UploadedFile object
            folder: Cloudinary folder path
            
        Returns:
            dict: {'url': cloudinary_url, 'public_id': public_id} or None on failure
        """
        try:
            if not image_file:
                return None

            # Ensure Cloudinary is configured
            if not settings.CLOUDINARY_CLOUD_NAME:
                logger.warning('Cloudinary not configured')
                return None

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                image_file,
                folder=folder,
                resource_type='image',
                quality='auto',
                fetch_format='auto',
                width=300,
                height=300,
                crop='fill',
                gravity='auto',
                overwrite=True,
                tags=['company', 'logo']
            )

            return {
                'url': result.get('secure_url', result.get('url')),
                'public_id': result.get('public_id')
            }

        except Exception as e:
            logger.error(f'Error uploading to Cloudinary: {str(e)}')
            return None

    @staticmethod
    def delete_logo(public_id):
        """
        Delete logo from Cloudinary
        
        Args:
            public_id: Cloudinary public_id of the image
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            if not public_id:
                return False

            if not settings.CLOUDINARY_CLOUD_NAME:
                logger.warning('Cloudinary not configured')
                return False

            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'

        except Exception as e:
            logger.error(f'Error deleting from Cloudinary: {str(e)}')
            return False

    @staticmethod
    def get_logo_url(logo_url):
        """
        Get optimized Cloudinary URL for logo
        
        Args:
            logo_url: URL string from database
            
        Returns:
            str: Optimized Cloudinary URL
        """
        if not logo_url:
            return None

        # If it's already a Cloudinary URL, return as is
        if 'cloudinary' in logo_url:
            return logo_url

        return logo_url


cloudinary_service = CloudinaryService()
