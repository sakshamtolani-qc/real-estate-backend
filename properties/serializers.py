from rest_framework import serializers
from .models import Property, PropertyImage, PropertyType, PropertyFeature


class PropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyType
        fields = ['id', 'name', 'description']


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'title', 'is_primary', 'order']


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
        """Get image URL, handling cases where image property returns None"""
        try:
            request = self.context.get('request')
            image_url = obj.image  # This is a property that might return None
            if image_url and request:
                # Only build absolute URI if image_url is not None
                return request.build_absolute_uri(image_url)
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
        if images and request:
            return [request.build_absolute_uri(img.image.url) for img in images]
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