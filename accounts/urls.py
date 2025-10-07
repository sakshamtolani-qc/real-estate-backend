from django.urls import path
from .views import (
    EmployeeListAPIView, 
    EmployeeDetailAPIView, 
    TopClosersAPIView, 
    ProfileAPIView,
    UserRegistrationAPIView,
    AddStaffAPIView
)

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('add-staff/', AddStaffAPIView.as_view(), name='add-staff'),
    path('list/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('detail/<int:pk>/', EmployeeDetailAPIView.as_view(), name='employee-detail'),
    path('top-closers/', TopClosersAPIView.as_view(), name='top-closers'),
    path('profile/', ProfileAPIView.as_view(), name='user-profile'),
]
