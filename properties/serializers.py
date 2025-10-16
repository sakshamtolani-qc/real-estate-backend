from rest_framework import serializers
from .models import Property, PropertyImage, PropertyType, PropertyFeature


class PropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyType
        fields = ['id', 'name', 'description']


class PropertyImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'title', 'is_primary', 'order']
    
    def get_image(self, obj):
        """Return image URL - handles both Cloudinary URLs and local paths"""
        if obj.image:
            image_str = str(obj.image)
            # If it's already a Cloudinary URL, return as is
            if image_str.startswith('http'):
                return image_str
            # If it's a local path, build absolute URI
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image_str)
            return image_str
        return None


class PropertyListSerializer(serializers.ModelSerializer):
    """Serializer for property list view - matches frontend BackendProperty interface"""
    id = serializers.CharField(source='pk')
    uuid = serializers.UUIDField(read_only=True)
    image = serializers.SerializerMethodField()
    type = serializers.CharField(source='property_type.name')
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'uuid', 'title', 'price', 'location', 'bedrooms', 
            'bathrooms', 'area', 'image', 'status', 'type', 'featured'
        ]
    
    def get_image(self, obj):
        """Get image URL, handling Cloudinary URLs and local paths"""
        try:
            image_url = obj.image  # This is a property that might return None
            if not image_url:
                return None
            
            image_str = str(image_url)
            # If it's already a Cloudinary URL, return as is
            if image_str.startswith('http'):
                return image_str
            
            # For local paths, build absolute URI
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image_str)
            return image_str
        except Exception as e:
            # Log error but don't fail the request
            print(f"Error getting image for property {obj.id}: {e}")
        # Return None to let frontend use its default images
        return None
    
    def get_status(self, obj):
        if obj.listing_type == 'sale':
            return 'FOR SALE'
        return 'FOR RENT'


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Serializer for property detail view - matches frontend BackendPropertyDetail interface"""
    id = serializers.CharField(source='pk')
    uuid = serializers.UUIDField(read_only=True)
    property_type = PropertyTypeSerializer(read_only=True)
    images = serializers.SerializerMethodField()
    listing_type = serializers.CharField()
    status = serializers.CharField()
    subtitle = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'uuid', 'title', 'description', 'property_type', 'listing_type',
            'status', 'address', 'city', 'state', 'zip_code', 'location',
            'bedrooms', 'bathrooms', 'square_feet', 'area', 'sale_price',
            'rent_price', 'price', 'images', 'has_pool', 'has_garden',
            'parking_spaces', 'featured', 'views_count', 'date_listed', 'subtitle'
        ]
    
    def get_images(self, obj):
        request = self.context.get('request')
        images = obj.images.all()
        image_urls = []
        
        if images:
            for img in images:
                image_str = str(img.image)
                # If it's a Cloudinary URL (starts with http), use as is
                if image_str.startswith('http'):
                    image_urls.append(image_str)
                # Otherwise, build absolute URI for local files
                elif request:
                    image_urls.append(request.build_absolute_uri(image_str))
                else:
                    image_urls.append(image_str)
            
            if image_urls:
                return image_urls
        
        # Return placeholder images if no images
        return ['/P1a.png', '/P1b.png', '/P1c.png', '/P1d-3.png', '/P1e-4.png']
    
    def get_subtitle(self, obj):
        return f"{obj.property_type.name} in {obj.city}"


class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating properties"""
    features = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ['uuid', 'date_listed', 'views_count']
    
    def create(self, validated_data):
        features = validated_data.pop('features', [])
        property_instance = super().create(validated_data)
        
        # Create features
        for feature_name in features:
            PropertyFeature.objects.create(
                property=property_instance,
                name=feature_name
            )
        
        return property_instance
    
    def update(self, instance, validated_data):
        features = validated_data.pop('features', None)
        property_instance = super().update(instance, validated_data)
        
        # Update features if provided
        if features is not None:
            property_instance.features.all().delete()
            for feature_name in features:
                PropertyFeature.objects.create(
                    property=property_instance,
                    name=feature_name
                )
        
        return property_instance