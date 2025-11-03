from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

from .views import (
    PropertyListAPIView, 
    PropertyDetailAPIView, 
    PropertyCreateAPIView,
    PropertyDeleteAPIView,
    PropertyTypesAPIView,
    DashboardStatsAPIView
)

urlpatterns = [
    path('list/', PropertyListAPIView.as_view(), name='property-list'),
    path('detail/<int:pk>/', PropertyDetailAPIView.as_view(), name='property-detail'),
    path('delete/<int:pk>/', PropertyDeleteAPIView.as_view(), name='property-delete'),
    path('create/', PropertyCreateAPIView.as_view(), name='property-create'),
    path('types/', PropertyTypesAPIView.as_view(), name='property-types'),
    path('dashboard-stats/', DashboardStatsAPIView.as_view(), name='dashboard-stats'),
]

# Admin dashboard routes under /api/admin/dashboard/
admin_dashboard_patterns = [
    path('stats/', DashboardStatsAPIView.as_view(), name='admin-dashboard-stats'),
]
