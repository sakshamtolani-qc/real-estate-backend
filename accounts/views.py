from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
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
    queryset = Employee.objects.select_related('user').all()
    serializer_class = EmployeeSerializer

class EmployeeDetailAPIView(generics.RetrieveAPIView):
    queryset = Employee.objects.select_related('user').all()
    serializer_class = EmployeeSerializer
