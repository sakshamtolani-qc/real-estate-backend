from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .settings_model import CompanySettings
from .settings_serializer import CompanySettingsSerializer
from .cloudinary_service import cloudinary_service
import logging

logger = logging.getLogger(__name__)


class CompanySettingsRetrieveAPIView(APIView):
    """Retrieve company settings - Public access"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            settings = CompanySettings.get_settings()
            serializer = CompanySettingsSerializer(settings, context={'request': request})
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompanySettingsUpdateAPIView(APIView):
    """Update company settings - Admin only"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    
    def put(self, request):
        try:
            settings = CompanySettings.get_settings()
            serializer = CompanySettingsSerializer(
                settings,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Settings updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request):
        """PATCH method - same as PUT but explicitly for partial updates"""
        return self.put(request)


class CompanySettingsAdminAPIView(APIView):
    """Combined view for retrieving and updating company settings"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request):
        """Get settings - allowed for authenticated users"""
        try:
            settings = CompanySettings.get_settings()
            serializer = CompanySettingsSerializer(settings, context={'request': request})
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Update settings - admin only"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({
                'success': False,
                'message': 'Only admins can update settings'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            settings_obj = CompanySettings.get_settings()
            
            # Handle logo upload to Cloudinary
            if 'logo' in request.FILES:
                logo_file = request.FILES['logo']
                cloudinary_result = cloudinary_service.upload_logo(logo_file)
                
                if cloudinary_result:
                    # Delete old logo from Cloudinary if it exists
                    if settings_obj.logo_url and 'cloudinary' in settings_obj.logo_url:
                        # Extract public_id from URL (optional, for cleanup)
                        pass
                    
                    # Update request data with Cloudinary URL
                    request.data._mutable = True
                    request.data['logo_url'] = cloudinary_result['url']
                    # Remove the file from data since we're using URL
                    if 'logo' in request.data:
                        del request.data['logo']
                    request.data._mutable = False
                else:
                    logger.warning('Failed to upload logo to Cloudinary')
            
            serializer = CompanySettingsSerializer(
                settings_obj,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Settings updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f'Error updating settings: {str(e)}')
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request):
        """PATCH method"""
        return self.put(request)
