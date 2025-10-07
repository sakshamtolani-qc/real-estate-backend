from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from leads.models import Lead, Deal
import decimal

class DashboardStatsAPIView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		from accounts.models import Employee
		# Get current month and last month dates
		now = datetime.now()
		start_of_month = datetime(now.year, now.month, 1)
		if now.month == 1:
			start_of_last_month = datetime(now.year - 1, 12, 1)
		else:
			start_of_last_month = datetime(now.year, now.month - 1, 1)
		
		# Calculate Total Revenue (completed deals this month)
		revenue_this_month = Deal.objects.filter(
			closing_date__gte=start_of_month,
			status='completed'
		).aggregate(total=Sum('amount'))['total'] or decimal.Decimal(0)
		
		revenue_last_month = Deal.objects.filter(
			closing_date__gte=start_of_last_month,
			closing_date__lt=start_of_month,
			status='completed'
		).aggregate(total=Sum('amount'))['total'] or decimal.Decimal(0)
		
		# Calculate trend
		if revenue_last_month > 0:
			revenue_trend = ((revenue_this_month - revenue_last_month) / revenue_last_month * 100)
			revenue_trend_str = f"{revenue_trend:+.1f}%"
		else:
			revenue_trend_str = "+100%" if revenue_this_month > 0 else "0%"
		
		# Format revenue for display
		if revenue_this_month >= 1000000:
			revenue_display = f"{int(revenue_this_month / 1000000)}M"
		elif revenue_this_month >= 1000:
			revenue_display = f"{int(revenue_this_month / 1000)}k"
		else:
			revenue_display = str(int(revenue_this_month))
		
		# New Leads this month
		new_leads_count = Lead.objects.filter(
			created_at__gte=start_of_month
		).count()
		
		# Offers Made (leads in proposal or negotiation stage)
		offers_count = Lead.objects.filter(
			Q(status='proposal') | Q(status='negotiation'),
			updated_at__gte=start_of_month
		).count()
		
		# Deals Closed this month
		deals_closed_this_month = Deal.objects.filter(
			closing_date__gte=start_of_month,
			status='completed'
		).count()
		
		deals_closed_last_month = Deal.objects.filter(
			closing_date__gte=start_of_last_month,
			closing_date__lt=start_of_month,
			status='completed'
		).count()
		
		# Calculate deals trend
		if deals_closed_last_month > 0:
			deals_trend = ((deals_closed_this_month - deals_closed_last_month) / deals_closed_last_month * 100)
			deals_trend_str = f"{deals_trend:+.1f}%"
		else:
			deals_trend_str = "+100%" if deals_closed_this_month > 0 else "0%"
		
		# --- Top Closers by number of assigned leads ---
		top_closers_qs = Employee.objects.annotate(
			lead_count=Count('leads')
		).order_by('-lead_count')[:5]
		top_closers = [
			{
				"name": emp.user.get_full_name() or emp.user.username,
				"lead_count": emp.lead_count
			} for emp in top_closers_qs if emp.lead_count > 0
		]
		# ---
		stats = [
			{
				"label": "Total Revenue", 
				"subtext": "This Month", 
				"value": revenue_display, 
				"trend": revenue_trend_str, 
				"color": "#8BC5B8"
			},
			{
				"label": "New Leads", 
				"subtext": "This Month", 
				"value": str(new_leads_count), 
				"color": "#FFB38A"
			},
			{
				"label": "Offers Made", 
				"subtext": "This Month", 
				"value": f"{offers_count / 1000:.1f}k" if offers_count >= 1000 else str(offers_count), 
				"color": "#F5D98E"
			},
			{
				"label": "Deals Closed", 
				"subtext": "This Month", 
				"value": str(deals_closed_this_month), 
				"trend": deals_trend_str, 
				"color": "#A5E8D8"
			}
		]
		return Response({"stats": stats, "top_closers": top_closers})
from rest_framework import generics
from .models import Property
from .serializers import PropertyListSerializer, PropertyDetailSerializer

class PropertyListAPIView(generics.ListAPIView):
	queryset = Property.objects.all()
	serializer_class = PropertyListSerializer

class PropertyDetailAPIView(generics.RetrieveAPIView):
	queryset = Property.objects.all()
	serializer_class = PropertyDetailSerializer
