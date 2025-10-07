from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .serializers import UserSerializer, UserRegistrationSerializer, AddStaffSerializer

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
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'is_employee': user.is_employee,
            'is_client': user.is_client,
            'is_superuser': user.is_superuser,
        })
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.http import JsonResponse
class TopClosersAPIView(APIView):
    def get(self, request):
        # For demo, use Employee objects and add a 'leads' field if available
        employees = Employee.objects.select_related('user').all()
        # If you have a Lead model, you can annotate with Count('lead')
        closers = []
        for emp in employees:
            closers.append({
                'name': emp.user.first_name or emp.user.username,
                'image': '/avatar_1.png',
                'deals': getattr(emp, 'leads', 0)  # Replace with actual lead count if available
            })
        # Sort by deals descending
        closers = sorted(closers, key=lambda x: x['deals'], reverse=True)[:3]
        return Response({'top_closers': closers})
from rest_framework import generics
from .models import Employee
from .serializers import EmployeeSerializer

class EmployeeListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]  # Allow access for now, can be restricted later
    queryset = Employee.objects.select_related('user').all().order_by('-date_joined')
    serializer_class = EmployeeSerializer

class EmployeeDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]  # Allow access for now, can be restricted later
    queryset = Employee.objects.select_related('user').all().order_by('-date_joined')
    serializer_class = EmployeeSerializer
