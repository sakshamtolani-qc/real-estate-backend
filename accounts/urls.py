from django.urls import path
from .views import EmployeeListAPIView, EmployeeDetailAPIView, TopClosersAPIView, ProfileAPIView

urlpatterns = [
    path('list/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('detail/<int:pk>/', EmployeeDetailAPIView.as_view(), name='employee-detail'),
    path('top-closers/', TopClosersAPIView.as_view(), name='top-closers'),
]
