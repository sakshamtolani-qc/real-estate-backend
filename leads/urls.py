from django.urls import path
from .views import (
    LeadSourcesAPIView, 
    LeadsListAPIView, 
    LeadCreateAPIView,
    LeadDetailAPIView,
    LeadUpdateAPIView,
    AgentsListAPIView
)
from .agent_stats_view import AgentDashboardStatsAPIView
from .scheduled_visit_views import (
    ScheduledVisitListAPIView,
    ScheduledVisitCreateAPIView,
    ScheduledVisitDeleteAPIView,
    ScheduledVisitUpdateAPIView
)

urlpatterns = [
    path('lead-sources/', LeadSourcesAPIView.as_view(), name='lead-sources'),
    path('list/', LeadsListAPIView.as_view(), name='leads-list'),
    path('create/', LeadCreateAPIView.as_view(), name='lead-create'),
    path('<int:lead_id>/', LeadDetailAPIView.as_view(), name='lead-detail'),
    path('<int:lead_id>/update/', LeadUpdateAPIView.as_view(), name='lead-update'),
    path('agents/', AgentsListAPIView.as_view(), name='agents-list'),
    path('agent/dashboard-stats/', AgentDashboardStatsAPIView.as_view(), name='agent-dashboard-stats'),
    # Scheduled Visits
    path('visits/', ScheduledVisitListAPIView.as_view(), name='visits-list'),
    path('visits/create/', ScheduledVisitCreateAPIView.as_view(), name='visit-create'),
    path('visits/<int:visit_id>/delete/', ScheduledVisitDeleteAPIView.as_view(), name='visit-delete'),
    path('visits/<int:visit_id>/update/', ScheduledVisitUpdateAPIView.as_view(), name='visit-update'),
]
