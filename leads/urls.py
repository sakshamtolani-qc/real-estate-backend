from django.urls import path
from .views import (
    LeadSourcesAPIView, 
    LeadsListAPIView, 
    LeadCreateAPIView,
    LeadDetailAPIView,
    LeadUpdateAPIView,
    AgentsListAPIView
)

urlpatterns = [
    path('lead-sources/', LeadSourcesAPIView.as_view(), name='lead-sources'),
    path('list/', LeadsListAPIView.as_view(), name='leads-list'),
    path('create/', LeadCreateAPIView.as_view(), name='lead-create'),
    path('<int:lead_id>/', LeadDetailAPIView.as_view(), name='lead-detail'),
    path('<int:lead_id>/update/', LeadUpdateAPIView.as_view(), name='lead-update'),
    path('agents/', AgentsListAPIView.as_view(), name='agents-list'),
]
