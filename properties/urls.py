from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

from .views import PropertyListAPIView, PropertyDetailAPIView, DashboardStatsAPIView

urlpatterns = [
    path('list/', PropertyListAPIView.as_view(), name='property-list'),
    path('detail/<int:pk>/', PropertyDetailAPIView.as_view(), name='property-detail'),
    path('dashboard-stats/', DashboardStatsAPIView.as_view(), name='dashboard-stats'),
]
