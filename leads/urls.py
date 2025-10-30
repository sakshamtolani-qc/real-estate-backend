from django.urls import path
from .views import (
    LeadSourcesAPIView, 
    LeadsListAPIView, 
    LeadCreateAPIView,
    LeadDetailAPIView,
    LeadUpdateAPIView,
    LeadDeleteAPIView,
    AgentsListAPIView,
    CloseLeadDealAPIView,
    ClosedDealsListAPIView
)
from .agent_stats_view import AgentDashboardStatsAPIView
from .scheduled_visit_views import (
    ScheduledVisitListAPIView,
    ScheduledVisitCreateAPIView,
    ScheduledVisitDeleteAPIView,
    ScheduledVisitUpdateAPIView
)
from .notification_views import (
    NotificationListAPIView,
    NotificationMarkReadAPIView,
    NotificationMarkAllReadAPIView,
    NotificationDeleteAPIView,
    NotificationCreateAPIView
)
from .contact_views import (
    ContactInquiryAPIView,
    CallScheduleAPIView,
    PropertyInquiryAPIView
)
from .settings_views import (
    CompanySettingsRetrieveAPIView,
    CompanySettingsUpdateAPIView,
    CompanySettingsAdminAPIView
)

urlpatterns = [
    path('lead-sources/', LeadSourcesAPIView.as_view(), name='lead-sources'),
    path('list/', LeadsListAPIView.as_view(), name='leads-list'),
    path('create/', LeadCreateAPIView.as_view(), name='lead-create'),
    path('<int:lead_id>/', LeadDetailAPIView.as_view(), name='lead-detail'),
    path('<int:lead_id>/update/', LeadUpdateAPIView.as_view(), name='lead-update'),
    path('<int:lead_id>/delete/', LeadDeleteAPIView.as_view(), name='lead-delete'),
    path('<int:lead_id>/close-deal/', CloseLeadDealAPIView.as_view(), name='close-lead-deal'),
    path('agents/', AgentsListAPIView.as_view(), name='agents-list'),
    path('deals/closed/', ClosedDealsListAPIView.as_view(), name='closed-deals-list'),
    path('agent/dashboard-stats/', AgentDashboardStatsAPIView.as_view(), name='agent-dashboard-stats'),
    # Scheduled Visits
    path('visits/', ScheduledVisitListAPIView.as_view(), name='visits-list'),
    path('visits/create/', ScheduledVisitCreateAPIView.as_view(), name='visit-create'),
    path('visits/<int:visit_id>/delete/', ScheduledVisitDeleteAPIView.as_view(), name='visit-delete'),
    path('visits/<int:visit_id>/update/', ScheduledVisitUpdateAPIView.as_view(), name='visit-update'),
    # Notifications
    path('notifications/', NotificationListAPIView.as_view(), name='notifications-list'),
    path('notifications/mark-read/', NotificationMarkReadAPIView.as_view(), name='notifications-mark-read'),
    path('notifications/mark-all-read/', NotificationMarkAllReadAPIView.as_view(), name='notifications-mark-all-read'),
    path('notifications/<int:notification_id>/delete/', NotificationDeleteAPIView.as_view(), name='notification-delete'),
    path('notifications/create/', NotificationCreateAPIView.as_view(), name='notification-create'),
    # Contact/Inquiry endpoints (public)
    path('contact/', ContactInquiryAPIView.as_view(), name='contact-inquiry'),
    path('schedule-call/', CallScheduleAPIView.as_view(), name='schedule-call'),
    path('property-inquiry/', PropertyInquiryAPIView.as_view(), name='property-inquiry'),
    # Settings endpoints
    path('settings/', CompanySettingsRetrieveAPIView.as_view(), name='company-settings'),
    path('settings/update/', CompanySettingsUpdateAPIView.as_view(), name='company-settings-update'),
    path('admin/settings/', CompanySettingsAdminAPIView.as_view(), name='company-settings-admin'),
]
