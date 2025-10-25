from rest_framework import serializers
from .settings_model import CompanySettings


class CompanySettingsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CompanySettings
        fields = [
            'id',
            'company_name',
            'country',
            'city',
            'address',
            'phone',
            'email',
            'about',
            'policies',
            'logo_url',
            'logo_public_id',
            'additional_emails',
            'additional_phones',
            'facebook_url',
            'twitter_url',
            'instagram_url',
            'linkedin_url',
            'business_hours',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'logo_public_id', 'created_at', 'updated_at']
    
    def get_logo_url(self, obj):
        """Get logo URL from Cloudinary"""
        if obj.logo_url:
            return obj.logo_url
        return None
