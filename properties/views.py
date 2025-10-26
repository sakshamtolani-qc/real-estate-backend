from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from leads.models import Lead, Deal
import decimal

class DashboardStatsAPIView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		from accounts.models import Employee
		from django.db import connection
		
		# Check if Lead and Deal tables exist
		tables = connection.introspection.table_names()
		has_lead_table = 'leads_lead' in tables
		has_deal_table = 'leads_deal' in tables
		
		# Get current month and last month dates
		now = datetime.now()
		start_of_month = datetime(now.year, now.month, 1)
		if now.month == 1:
			start_of_last_month = datetime(now.year - 1, 12, 1)
		else:
			start_of_last_month = datetime(now.year, now.month - 1, 1)
		
		# Calculate Total Revenue (completed deals this month) - only if table exists
		if has_deal_table:
			try:
				revenue_this_month = Deal.objects.filter(
					closing_date__gte=start_of_month,
					status='completed'
				).aggregate(total=Sum('amount'))['total'] or decimal.Decimal(0)
				
				revenue_last_month = Deal.objects.filter(
					closing_date__gte=start_of_last_month,
					closing_date__lt=start_of_month,
					status='completed'
				).aggregate(total=Sum('amount'))['total'] or decimal.Decimal(0)
			except Exception as e:
				revenue_this_month = decimal.Decimal(0)
				revenue_last_month = decimal.Decimal(0)
		else:
			revenue_this_month = decimal.Decimal(0)
			revenue_last_month = decimal.Decimal(0)
		
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
		
		# New Leads this month - only if table exists
		if has_lead_table:
			try:
				new_leads_count = Lead.objects.filter(
					created_at__gte=start_of_month,
					status='new'
				).count()
				
				# Offers Made (leads in proposal or negotiation stage)
				offers_count = Lead.objects.filter(
					Q(status='proposal') | Q(status='negotiation'),
					updated_at__gte=start_of_month
				).count()
			except Exception as e:
				new_leads_count = 0
				offers_count = 0
		else:
			new_leads_count = 0
			offers_count = 0
		
		# Deals Closed this month - only if table exists
		if has_deal_table:
			try:
				deals_closed_this_month = Deal.objects.filter(
					closing_date__gte=start_of_month,
					status='completed'
				).count()
				
				deals_closed_last_month = Deal.objects.filter(
					closing_date__gte=start_of_last_month,
					closing_date__lt=start_of_month,
					status='completed'
				).count()
			except Exception as e:
				deals_closed_this_month = 0
				deals_closed_last_month = 0
		else:
			deals_closed_this_month = 0
			deals_closed_last_month = 0
		
		# Calculate deals trend
		if deals_closed_last_month > 0:
			deals_trend = ((deals_closed_this_month - deals_closed_last_month) / deals_closed_last_month * 100)
			deals_trend_str = f"{deals_trend:+.1f}%"
		else:
			deals_trend_str = "+100%" if deals_closed_this_month > 0 else "0%"
		
		# --- Top Closers by number of assigned leads ---
		if has_lead_table:
			try:
				top_closers_qs = Employee.objects.select_related('user').annotate(
					lead_count=Count('leads')
				).order_by('-lead_count')[:3]
				top_closers = [
					{
						"id": emp.id,
						"user_id": emp.user.id,
						"name": emp.user.get_full_name() or emp.user.username,
						"email": emp.user.email,
						"phone": emp.user.phone,
						"profile_photo_url": getattr(emp.user, 'profile_photo_url', None),
						"deals": emp.lead_count
					} for emp in top_closers_qs if emp.lead_count > 0
				]
			except Exception as e:
				top_closers = []
		else:
			top_closers = []
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
from rest_framework import generics, status as drf_status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Property, PropertyType, PropertyImage
from .serializers import PropertyListSerializer, PropertyDetailSerializer, PropertyCreateUpdateSerializer

class PropertyListAPIView(generics.ListAPIView):
	permission_classes = [AllowAny]  # Allow anyone to view properties
	queryset = Property.objects.select_related('property_type').prefetch_related('images').all()
	serializer_class = PropertyListSerializer
	pagination_class = None  # Disable pagination for now, or configure if needed
	
	def get_serializer_context(self):
		"""Pass request context to serializer"""
		context = super().get_serializer_context()
		context['request'] = self.request
		return context

class PropertyDetailAPIView(generics.RetrieveAPIView):
	permission_classes = [AllowAny]  # Allow anyone to view property details
	queryset = Property.objects.select_related('property_type').prefetch_related('images').all()
	serializer_class = PropertyDetailSerializer

class PropertyCreateAPIView(APIView):
	"""Allow authenticated users (agents/admin) to create property listings"""
	permission_classes = [IsAuthenticated]
	parser_classes = [MultiPartParser, FormParser]
	
	def post(self, request):
		try:
			# For FormData, use request.data (DRF handles it properly)
			data = request.data
			
			# Validate required fields
			required_fields = ['title', 'property_type_id', 'listing_type', 'location', 'description']
			for field in required_fields:
				if not data.get(field):
					return Response({
						'success': False,
						'message': f'{field.replace("_", " ").title()} is required'
					}, status=drf_status.HTTP_400_BAD_REQUEST)
			
			# Get property type
			try:
				property_type = PropertyType.objects.get(id=data['property_type_id'])
			except PropertyType.DoesNotExist:
				return Response({
					'success': False,
					'message': 'Invalid property type'
				}, status=drf_status.HTTP_400_BAD_REQUEST)
			
			# Set pricing based on listing type
			sale_price = None
			rent_price = None
			price_display = data.get('price', '')
			
			if data['listing_type'] == 'sale':
				sale_price = data.get('sale_price', '')
				if not sale_price or sale_price == '':
					return Response({
						'success': False,
						'message': 'Sale price is required for sale listings'
					}, status=drf_status.HTTP_400_BAD_REQUEST)
				if not price_display:
					price_display = f"₹{int(float(sale_price)):,}"
			elif data['listing_type'] == 'rent':
				rent_price = data.get('rent_price', '')
				if not rent_price or rent_price == '':
					return Response({
						'success': False,
						'message': 'Rent price is required for rent listings'
					}, status=drf_status.HTTP_400_BAD_REQUEST)
				if not price_display:
					price_display = f"₹{int(float(rent_price)):,}/month"
			
			# Calculate display area
			square_feet_value = data.get('square_feet', '0')
			square_feet = int(square_feet_value) if square_feet_value and str(square_feet_value).strip() else 0
			area_display = data.get('area', '')
			if not area_display:
				if square_feet > 0:
					area_display = f"{square_feet} sqft"
				else:
					area_display = "0 sqft"
			
			# Create property with safe type conversions
			bedrooms_val = data.get('bedrooms', '0')
			bathrooms_val = data.get('bathrooms', '0')
			parking_val = data.get('parking_spaces', '0')
			
			property_obj = Property.objects.create(
				title=str(data['title']),
				property_type=property_type,
				listing_type=str(data['listing_type']),
				status=str(data.get('status', 'available')),
				address=str(data.get('address', data['location'])),
				city=str(data.get('city', '')),
				state=str(data.get('state', '')),
				zip_code=str(data.get('zip_code', '')),
				location=str(data['location']),
				bedrooms=int(bedrooms_val) if str(bedrooms_val).strip() and str(bedrooms_val) != '' else 0,
				bathrooms=int(bathrooms_val) if str(bathrooms_val).strip() and str(bathrooms_val) != '' else 0,
				square_feet=square_feet,
				area=str(area_display),
				parking_spaces=int(parking_val) if str(parking_val).strip() and str(parking_val) != '' else 0,
				furnished_status=str(data.get('furnished_status', '')),
				sale_price=sale_price if sale_price and sale_price != '' else None,
				rent_price=rent_price if rent_price and rent_price != '' else None,
				price=str(price_display),
				has_pool=str(data.get('has_pool', 'false')).lower() == 'true',
				has_garden=str(data.get('has_garden', 'false')).lower() == 'true',
				description=str(data['description']),
				featured=str(data.get('featured', 'false')).lower() == 'true',
			)
			
			# Handle image uploads
			images = request.FILES.getlist('images')
			if images:
				for index, image in enumerate(images):
					PropertyImage.objects.create(
						property=property_obj,
						image=image,
						title=f"{property_obj.title} - Image {index + 1}",
						is_primary=(index == 0),  # First image is primary
						order=index
					)
			
			return Response({
				'success': True,
				'message': 'Property created successfully!',
				'property_id': property_obj.id,
				'property': {
					'id': property_obj.id,
					'uuid': str(property_obj.uuid),
					'title': property_obj.title,
					'location': property_obj.location,
					'price': property_obj.price
				}
			}, status=drf_status.HTTP_201_CREATED)
			
		except Exception as e:
			import traceback
			print(f"Error creating property: {str(e)}")
			print(traceback.format_exc())
			return Response({
				'success': False,
				'message': f'Error creating property: {str(e)}'
			}, status=drf_status.HTTP_400_BAD_REQUEST)

class PropertyTypesAPIView(APIView):
	"""Get list of all property types"""
	permission_classes = [IsAuthenticated]
	
	def get(self, request):
		try:
			property_types = PropertyType.objects.all()
			types_data = [{
				'id': pt.id,
				'name': pt.name,
				'description': pt.description
			} for pt in property_types]
			
			return Response({
				'results': types_data,
				'count': len(types_data)
			})
		except Exception as e:
			return Response({
				'message': str(e)
			}, status=drf_status.HTTP_400_BAD_REQUEST)
