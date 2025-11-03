from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()

class EmailTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        try:
            user = User.objects.filter(email=email).first()
            if user is None:
                raise serializers.ValidationError('No user with this email.')
            user = authenticate(username=user.username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
        except Exception as e:
            raise serializers.ValidationError(f'Authentication failed: {str(e)}')
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        # Determine user role explicitly
        role = 'customer'  # default
        if user.is_superuser:
            role = 'admin'
        elif user.is_employee:
            role = 'agent'
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'is_employee': user.is_employee,
                'is_client': user.is_client,
                'is_superuser': user.is_superuser,
                'role': role,  # Add explicit role field
            }
        }

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
