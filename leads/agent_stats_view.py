from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from datetime import datetime, timedelta
from .models import Lead, Deal
from accounts.models import Employee


class AgentDashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get current month dates
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        
        try:
            # Get the employee record for this agent
            employee = Employee.objects.get(user=user)
            
            # Get leads assigned to this agent or created by them
            my_leads = Lead.objects.filter(
                Q(assigned_to=employee) | Q(created_by=user)
            ).distinct()
            
            # New leads this month
            new_leads_count = my_leads.filter(
                created_at__gte=start_of_month,
                status='new'
            ).count()
            
            # All my leads
            total_my_leads = my_leads.count()
            
            # Leads in proposal or negotiation (offers made)
            offers_count = my_leads.filter(
                Q(status='proposal') | Q(status='negotiation')
            ).count()
            
            # Check if Deal model exists and get deals closed by this agent
            try:
                deals_closed_count = Deal.objects.filter(
                    closed_by=employee,
                    closing_date__gte=start_of_month,
                    status='completed'
                ).count()
            except:
                deals_closed_count = 0
            
            # Recent leads (top 5 for dashboard table)
            recent_leads = my_leads.order_by('-created_at')[:5]
            recent_leads_data = []
            for lead in recent_leads:
                recent_leads_data.append({
                    'id': lead.id,
                    'name': f"{lead.first_name} {lead.last_name}",
                    'phone': lead.phone,
                    'email': lead.email,
                    'status': lead.status,
                    'created_at': lead.created_at.isoformat(),
                })
            
            stats = {
                'new_leads': new_leads_count,
                'total_leads': total_my_leads,
                'offers_made': offers_count,
                'deals_closed': deals_closed_count,
                'recent_leads': recent_leads_data,
            }
            
            return Response(stats)
            
        except Employee.DoesNotExist:
            # User is not an employee/agent
            return Response({
                'new_leads': 0,
                'total_leads': 0,
                'offers_made': 0,
                'deals_closed': 0,
                'recent_leads': [],
            })
