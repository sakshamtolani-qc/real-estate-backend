from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from .models import ScheduledVisit, Lead
from properties.models import Property
from accounts.models import Employee


class ScheduledVisitListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all scheduled visits for the current agent"""
        user = request.user
        
        # Get upcoming visits (next 30 days)
        today = datetime.now().date()
        end_date = today + timedelta(days=30)
        
        visits = ScheduledVisit.objects.filter(
            agent=user,
            visit_date__gte=today,
            visit_date__lte=end_date,
            status='scheduled'
        ).order_by('visit_date', 'start_time')
        
        visits_data = []
        for visit in visits:
            visit_data = {
                'id': visit.id,
                'title': visit.title,
                'description': visit.description,
                'visit_date': visit.visit_date.isoformat(),
                'start_time': visit.start_time.strftime('%H:%M'),
                'end_time': visit.end_time.strftime('%H:%M'),
                'location': visit.location,
                'participants': visit.participants,
                'is_recurring': visit.is_recurring,
                'recurring_days': visit.recurring_days,
                'status': visit.status,
                'lead_id': visit.lead.id if visit.lead else None,
                'property_id': visit.property.id if visit.property else None,
            }
            
            # Add lead details
            if visit.lead:
                visit_data['lead'] = {
                    'id': visit.lead.id,
                    'name': visit.lead.full_name,
                    'email': visit.lead.email,
                    'phone': visit.lead.phone,
                }
            else:
                visit_data['lead'] = None
            
            # Add property details
            if visit.property:
                visit_data['property'] = {
                    'id': visit.property.id,
                    'title': visit.property.title,
                    'address': visit.property.address,
                    'city': visit.property.city,
                }
            else:
                visit_data['property'] = None
            
            visits_data.append(visit_data)
        
        return Response({
            'results': visits_data,
            'count': len(visits_data)
        })


class ScheduledVisitCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a new scheduled visit"""
        data = request.data
        user = request.user
        
        try:
            # Parse dates and times
            visit_date = datetime.strptime(data.get('visit_date'), '%Y-%m-%d').date()
            start_time = datetime.strptime(data.get('start_time'), '%H:%M').time()
            end_time = datetime.strptime(data.get('end_time'), '%H:%M').time()
            
            # Get lead and property if provided
            lead = None
            property_obj = None
            
            if data.get('lead_id'):
                lead = Lead.objects.filter(id=data.get('lead_id')).first()
            
            if data.get('property_id'):
                property_obj = Property.objects.filter(id=data.get('property_id')).first()
            
            # Auto-generate title if not provided
            title = data.get('title')
            if not title:
                if lead and property_obj:
                    title = f"Visit with {lead.full_name} for {property_obj.title}"
                elif lead:
                    title = f"Visit with {lead.full_name}"
                elif property_obj:
                    title = f"Visit to {property_obj.title}"
                else:
                    title = "Property Visit"
            
            # Auto-generate location from property if not provided
            location = data.get('location', '')
            if not location and property_obj:
                location = f"{property_obj.address}, {property_obj.city}"
            
            # Create the visit
            visit = ScheduledVisit.objects.create(
                agent=user,
                lead=lead,
                property=property_obj,
                title=title,
                description=data.get('description', ''),
                visit_date=visit_date,
                start_time=start_time,
                end_time=end_time,
                location=location,
                participants=data.get('participants', ''),
                is_recurring=data.get('is_recurring', False),
                recurring_days=data.get('recurring_days', ''),
            )
            
            return Response({
                'message': 'Visit scheduled successfully',
                'visit_id': visit.id,
                'visit': {
                    'id': visit.id,
                    'title': visit.title,
                    'visit_date': visit.visit_date.isoformat(),
                    'start_time': visit.start_time.strftime('%H:%M'),
                    'end_time': visit.end_time.strftime('%H:%M'),
                    'location': visit.location,
                    'lead_id': visit.lead.id if visit.lead else None,
                    'property_id': visit.property.id if visit.property else None,
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'message': f'Error creating visit: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class ScheduledVisitDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, visit_id):
        """Delete a scheduled visit"""
        try:
            visit = get_object_or_404(ScheduledVisit, id=visit_id, agent=request.user)
            visit.delete()
            
            return Response({
                'message': 'Visit deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'message': f'Error deleting visit: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class ScheduledVisitUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, visit_id):
        """Update a scheduled visit"""
        try:
            visit = get_object_or_404(ScheduledVisit, id=visit_id, agent=request.user)
            data = request.data
            
            # Update fields if provided
            if 'title' in data:
                visit.title = data['title']
            if 'description' in data:
                visit.description = data['description']
            if 'visit_date' in data:
                visit.visit_date = datetime.strptime(data['visit_date'], '%Y-%m-%d').date()
            if 'start_time' in data:
                visit.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            if 'end_time' in data:
                visit.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
            if 'location' in data:
                visit.location = data['location']
            if 'participants' in data:
                visit.participants = data['participants']
            if 'status' in data:
                visit.status = data['status']
            
            visit.save()
            
            return Response({
                'message': 'Visit updated successfully',
                'visit_id': visit.id
            })
            
        except Exception as e:
            return Response({
                'message': f'Error updating visit: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
