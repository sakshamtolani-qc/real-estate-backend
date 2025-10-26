from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UserSerializer, UserRegistrationSerializer, AddStaffSerializer, EmployeeDetailSerializer
from .models import User, Employee

class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddStaffAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can add staff
    
    def post(self, request):
        serializer = AddStaffSerializer(data=request.data)
        if serializer.is_valid():
            employee = serializer.save()
            return Response({
                'message': 'Staff member added successfully',
                'employee': {
                    'id': employee.id,
                    'user': {
                        'id': employee.user.id,
                        'email': employee.user.email,
                        'first_name': employee.user.first_name,
                        'last_name': employee.user.last_name,
                        'phone': employee.user.phone
                    },
                    'status': employee.status,
                    'date_joined': employee.date_joined
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update user profile with support for file uploads"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_employee': user.is_employee,
                'is_client': user.is_client,
                'is_superuser': user.is_superuser,
                'profile_photo_url': user.profile_photo_url,
                'city': user.city,
                'country': user.country,
                'address': user.address,
                'about': user.about
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TopClosersAPIView(APIView):
    def get(self, request):
        from django.db.models import Count
        from leads.models import Lead
        employees = Employee.objects.select_related('user').annotate(
            lead_count=Count('leads')
        ).order_by('-lead_count')[:3]
        closers = []
        for emp in employees:
            closers.append({
                'id': emp.user.id,
                'name': emp.user.first_name or emp.user.username,
                'email': emp.user.email,
                'phone': emp.user.phone,
                'profile_photo_url': emp.user.profile_photo_url,
                'deals': emp.lead_count,
                'lead_count': emp.lead_count
            })
        return Response({'top_closers': closers})

class EmployeeListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Employee.objects.select_related('user').all().order_by('-date_joined')
    serializer_class = EmployeeDetailSerializer

class EmployeeDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Employee.objects.select_related('user').all()
    serializer_class = EmployeeDetailSerializer
