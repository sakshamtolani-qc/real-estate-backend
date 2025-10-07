from django.urls import path
from .views import LeadSourcesAPIView

urlpatterns = [
    path('lead-sources/', LeadSourcesAPIView.as_view(), name='lead-sources'),
]