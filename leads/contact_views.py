from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Lead, LeadSource, Notification
from accounts.models import User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ContactInquiryAPIView(APIView):
    """
    Handle contact form submissions from landing page
    Creates a lead and notifies all admins and agents
    """
    permission_classes = []  # Public endpoint
    
    def post(self, request):
        try:
            data = request.data
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'phone']
            for field in required_fields:
                if not data.get(field):
                    return Response({
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create "Website" lead source
            lead_source, created = LeadSource.objects.get_or_create(
                name='Website',
                defaults={'description': 'Leads from website contact form'}
            )
            
            # Check if lead already exists
            existing_lead = Lead.objects.filter(
                email=data.get('email')
            ).first()
            
            if existing_lead:
                return Response({
                    'success': True,
                    'message': 'Thank you! We already have your information and will contact you soon.',
                    'lead_id': existing_lead.id
                })
            
            # Create the lead
            lead = Lead.objects.create(
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                email=data.get('email'),
                phone=data.get('phone'),
                source=lead_source,
                notes=data.get('message', ''),
                status='new',
                budget_min=data.get('budget_min') if data.get('budget_min') else None,
                budget_max=data.get('budget_max') if data.get('budget_max') else None
            )
            
            # Notification is automatically created by signal
            # But we'll log it
            logger.info(f'New lead created from website: {lead.full_name} ({lead.email})')
            
            return Response({
                'success': True,
                'message': 'Thank you for contacting us! We will get back to you soon.',
                'lead_id': lead.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f'Error creating lead from contact form: {str(e)}')
            return Response({
                'success': False,
                'message': 'An error occurred while processing your request. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CallScheduleAPIView(APIView):
    """
    Handle call scheduling requests from landing page
    Creates a lead (if new) and notifies admins/agents about the scheduled call
    """
    permission_classes = []  # Public endpoint
    
    def post(self, request):
        try:
            data = request.data
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'phone', 'preferred_date', 'preferred_time']
            for field in required_fields:
                if not data.get(field):
                    return Response({
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create "Website" lead source
            lead_source, created = LeadSource.objects.get_or_create(
                name='Website',
                defaults={'description': 'Leads from website contact form'}
            )
            
            # Check if lead already exists
            lead = Lead.objects.filter(email=data.get('email')).first()
            
            if not lead:
                # Create new lead
                lead = Lead.objects.create(
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    email=data.get('email'),
                    phone=data.get('phone'),
                    source=lead_source,
                    notes=f"Requested call on {data.get('preferred_date')} at {data.get('preferred_time')}",
                    status='new',
                    budget_min=data.get('budget_min') if data.get('budget_min') else None,
                    budget_max=data.get('budget_max') if data.get('budget_max') else None
                )
            
            # Create call scheduling notification for all admins and agents
            # Get staff users (admins) and employees (agents)
            users = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True) | Q(is_employee=True))
            
            for user in users:
                Notification.objects.create(
                    recipient=user,
                    notification_type='call_scheduled',
                    title='Call Requested',
                    message=f'{lead.full_name} requested a call on {data.get("preferred_date")} at {data.get("preferred_time")}',
                    related_data={
                        'lead_id': lead.id,
                        'lead_name': lead.full_name,
                        'lead_email': lead.email,
                        'lead_phone': lead.phone,
                        'preferred_date': data.get('preferred_date'),
                        'preferred_time': data.get('preferred_time'),
                        'message': data.get('message', '')
                    },
                    action_url='/admin/leads' if (user.is_staff or user.is_superuser) else '/agent/leads'
                )
            
            logger.info(f'Call scheduled for lead: {lead.full_name} on {data.get("preferred_date")} at {data.get("preferred_time")}')
            
            return Response({
                'success': True,
                'message': 'Thank you! Your call has been scheduled. We will contact you at the requested time.',
                'lead_id': lead.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f'Error scheduling call: {str(e)}')
            return Response({
                'success': False,
                'message': 'An error occurred while scheduling your call. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PropertyInquiryAPIView(APIView):
    """
    Handle property-specific inquiries from landing page
    """
    permission_classes = []  # Public endpoint
    
    def post(self, request):
        try:
            data = request.data
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'phone', 'property_id']
            for field in required_fields:
                if not data.get(field):
                    return Response({
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create "Website" lead source
            lead_source, created = LeadSource.objects.get_or_create(
                name='Website',
                defaults={'description': 'Leads from website contact form'}
            )
            
            # Check if lead already exists
            lead = Lead.objects.filter(email=data.get('email')).first()
            
            property_id = data.get('property_id')
            
            if not lead:
                # Create new lead
                lead = Lead.objects.create(
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    email=data.get('email'),
                    phone=data.get('phone'),
                    source=lead_source,
                    notes=f"Interested in property ID: {property_id}\n{data.get('message', '')}",
                    status='new',
                    budget_min=data.get('budget_min') if data.get('budget_min') else None,
                    budget_max=data.get('budget_max') if data.get('budget_max') else None
                )
            
            # Create property inquiry notification for all admins and agents
            # Get staff users (admins) and employees (agents)
            users = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True) | Q(is_employee=True))
            
            for user in users:
                Notification.objects.create(
                    recipient=user,
                    notification_type='customer_signup',
                    title='Property Inquiry',
                    message=f'{lead.full_name} is interested in property #{property_id}',
                    related_data={
                        'lead_id': lead.id,
                        'lead_name': lead.full_name,
                        'lead_email': lead.email,
                        'lead_phone': lead.phone,
                        'property_id': property_id,
                        'message': data.get('message', '')
                    },
                    action_url='/admin/leads' if (user.is_staff or user.is_superuser) else '/agent/leads'
                )
            
            logger.info(f'Property inquiry from {lead.full_name} for property #{property_id}')
            
            return Response({
                'success': True,
                'message': 'Thank you for your interest! We will contact you shortly with more information.',
                'lead_id': lead.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f'Error processing property inquiry: {str(e)}')
            return Response({
                'success': False,
                'message': 'An error occurred while processing your inquiry. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
