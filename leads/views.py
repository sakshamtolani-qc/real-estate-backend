from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Lead, LeadSource, LeadNote
from accounts.models import Employee

class LeadSourcesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Dummy data, replace with real aggregation logic
        lead_sources = [
            {"source": "Email", "percentage": 50, "color": "#212121"},
            {"source": "Website", "percentage": 43, "color": "#E7C873"},
            {"source": "Phone", "percentage": 37, "color": "#D4AF37"},
            {"source": "Physical", "percentage": 37, "color": "#B794D6"},
            {"source": "Other", "percentage": 37, "color": "#7DD3E8"}
        ]
        return Response({"lead_sources": lead_sources})


class LeadsListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Check if user is admin/superuser - they can see all leads
        if user.is_superuser or user.is_staff:
            leads = Lead.objects.select_related('assigned_to__user', 'source').all()
        else:
            # For agents/employees - filter to show only leads assigned to them or created by them
            try:
                employee = Employee.objects.get(user=user)
                # Get leads assigned to this employee OR created by this user
                from django.db.models import Q
                leads = Lead.objects.select_related('assigned_to__user', 'source').filter(
                    Q(assigned_to=employee) | Q(created_by=user)
                ).distinct()
            except Employee.DoesNotExist:
                # User is not an employee, return empty list
                leads = Lead.objects.none()
        
        leads_data = []
        for lead in leads:
            lead_dict = {
                'id': lead.id,
                'first_name': lead.first_name,
                'last_name': lead.last_name,
                'email': lead.email,
                'phone': lead.phone,
                'budget_min': str(lead.budget_min) if lead.budget_min else None,
                'budget_max': str(lead.budget_max) if lead.budget_max else None,
                'status': lead.status,
                'source': lead.source.name if lead.source else None,
                'assigned_to': {
                    'id': lead.assigned_to.id if lead.assigned_to else None,
                    'user': {
                        'first_name': lead.assigned_to.user.first_name if lead.assigned_to else '',
                        'last_name': lead.assigned_to.user.last_name if lead.assigned_to else '',
                        'username': lead.assigned_to.user.username if lead.assigned_to else '',
                    }
                } if lead.assigned_to else None,
                'created_by': {
                    'id': lead.created_by.id if lead.created_by else None,
                    'first_name': lead.created_by.first_name if lead.created_by else '',
                    'last_name': lead.created_by.last_name if lead.created_by else '',
                    'username': lead.created_by.username if lead.created_by else '',
                } if lead.created_by else None,
                'created_at': lead.created_at,
                'updated_at': lead.updated_at,
            }
            leads_data.append(lead_dict)
        
        return Response({
            'results': leads_data,
            'count': len(leads_data)
        })


class LeadCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data
        
        try:
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'phone']
            for field in required_fields:
                if not data.get(field):
                    return Response({
                        'success': False,
                        'message': f'{field.replace("_", " ").title()} is required'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check for duplicate email
            email = data.get('email')
            existing_lead = Lead.objects.filter(email=email).first()
            if existing_lead:
                return Response({
                    'success': False,
                    'message': f'A lead with email {email} already exists. Please check the existing leads list.',
                    'existing_lead_id': existing_lead.id
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create default lead source
            source, _ = LeadSource.objects.get_or_create(
                name='Website',
                defaults={'description': 'Direct website inquiry'}
            )
            
            # Get assigned agent if provided, otherwise auto-assign to current user if they're an agent
            assigned_to = None
            if data.get('assigned_to'):
                try:
                    assigned_to = Employee.objects.get(id=data['assigned_to'])
                except Employee.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'Selected agent not found'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # If no agent assigned and user is not admin, auto-assign to current user
                if not (request.user.is_superuser or request.user.is_staff):
                    try:
                        assigned_to = Employee.objects.get(user=request.user)
                    except Employee.DoesNotExist:
                        pass
            
            # Create the lead
            lead = Lead.objects.create(
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                email=email,
                phone=data.get('phone'),
                budget_min=data.get('budget_min'),
                budget_max=data.get('budget_max'),
                status=data.get('status', 'new'),
                source=source,
                assigned_to=assigned_to,
                created_by=request.user,  # Track who created this lead
            )
            
            return Response({
                'success': True,
                'message': 'Lead created successfully!',
                'lead_id': lead.id,
                'lead': {
                    'id': lead.id,
                    'first_name': lead.first_name,
                    'last_name': lead.last_name,
                    'email': lead.email,
                    'phone': lead.phone
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error creating lead: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class LeadDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, lead_id):
        try:
            user = request.user
            
            # Get the lead
            lead = get_object_or_404(Lead.objects.select_related('assigned_to__user', 'source'), id=lead_id)
            
            # Check permissions - admins can see all, agents can only see their assigned/created leads or unassigned leads
            if not (user.is_superuser or user.is_staff):
                try:
                    employee = Employee.objects.get(user=user)
                    # Check if lead is assigned to this employee, created by this user, or is unassigned (available for agents to take)
                    if lead.assigned_to != employee and lead.created_by != user and lead.assigned_to is not None:
                        return Response({
                            'message': 'You do not have permission to view this lead'
                        }, status=status.HTTP_403_FORBIDDEN)
                except Employee.DoesNotExist:
                    return Response({
                        'message': 'You do not have permission to view this lead'
                    }, status=status.HTTP_403_FORBIDDEN)
            
            # Get all notes for this lead
            notes = lead.lead_notes.all()
            notes_data = []
            for note in notes:
                notes_data.append({
                    'id': note.id,
                    'note': note.note,
                    'created_at': note.created_at.isoformat(),
                    'created_by': note.created_by.username if note.created_by else 'Unknown',
                })
            
            lead_data = {
                'id': lead.id,
                'first_name': lead.first_name,
                'last_name': lead.last_name,
                'email': lead.email,
                'phone': lead.phone,
                'budget_min': str(lead.budget_min) if lead.budget_min else None,
                'budget_max': str(lead.budget_max) if lead.budget_max else None,
                'status': lead.status,
                'source': lead.source.name if lead.source else None,
                'notes': lead.notes,
                'notes_history': notes_data,
                'follow_up_date': lead.follow_up_date.isoformat() if lead.follow_up_date else None,
                'assigned_to': {
                    'id': lead.assigned_to.id if lead.assigned_to else None,
                    'user': {
                        'first_name': lead.assigned_to.user.first_name if lead.assigned_to else '',
                        'last_name': lead.assigned_to.user.last_name if lead.assigned_to else '',
                        'username': lead.assigned_to.user.username if lead.assigned_to else '',
                    }
                } if lead.assigned_to else None,
                'created_by': {
                    'id': lead.created_by.id if lead.created_by else None,
                    'first_name': lead.created_by.first_name if lead.created_by else '',
                    'last_name': lead.created_by.last_name if lead.created_by else '',
                    'username': lead.created_by.username if lead.created_by else '',
                } if lead.created_by else None,
                'created_at': lead.created_at,
                'updated_at': lead.updated_at,
            }
            
            return Response(lead_data)
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class LeadUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, lead_id):
        try:
            user = request.user
            lead = get_object_or_404(Lead, id=lead_id)
            
            # Check permissions - admins can update all, agents can only update their assigned/created leads or unassigned leads
            if not (user.is_superuser or user.is_staff):
                try:
                    employee = Employee.objects.get(user=user)
                    # Check if lead is assigned to this employee, created by this user, or is unassigned (available for agents to take)
                    if lead.assigned_to != employee and lead.created_by != user and lead.assigned_to is not None:
                        return Response({
                            'message': 'You do not have permission to update this lead'
                        }, status=status.HTTP_403_FORBIDDEN)
                except Employee.DoesNotExist:
                    return Response({
                        'message': 'You do not have permission to update this lead'
                    }, status=status.HTTP_403_FORBIDDEN)
            
            data = request.data
            
            # Update basic fields
            if 'first_name' in data:
                lead.first_name = data['first_name']
            if 'last_name' in data:
                lead.last_name = data['last_name']
            if 'email' in data:
                lead.email = data['email']
            if 'phone' in data:
                lead.phone = data['phone']
            if 'status' in data:
                lead.status = data['status']
            if 'notes' in data and data['notes'].strip():
                # Create a new note entry
                LeadNote.objects.create(
                    lead=lead,
                    note=data['notes'],
                    created_by=request.user if request.user.is_authenticated else None
                )
                # Also update the main notes field
                lead.notes = data['notes']
            if 'follow_up_date' in data:
                lead.follow_up_date = data['follow_up_date'] if data['follow_up_date'] else None
            
            # Update assigned agent
            if 'assigned_to' in data:
                if data['assigned_to']:
                    try:
                        agent = Employee.objects.get(id=data['assigned_to'])
                        lead.assigned_to = agent
                    except Employee.DoesNotExist:
                        return Response({
                            'message': 'Invalid agent ID'
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    lead.assigned_to = None
            
            lead.save()
            
            return Response({
                'message': 'Lead updated successfully',
                'lead_id': lead.id
            })
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class LeadDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, lead_id):
        try:
            user = request.user
            lead = get_object_or_404(Lead, id=lead_id)
            
            # Check permissions - only admins can delete leads
            # Or allow agents to delete their own created leads (optional)
            if not (user.is_superuser or user.is_staff):
                # Optional: Allow agents to delete leads they created
                if lead.created_by != user:
                    return Response({
                        'message': 'You do not have permission to delete this lead'
                    }, status=status.HTTP_403_FORBIDDEN)
            
            lead_name = f"{lead.first_name} {lead.last_name}"
            lead.delete()
            
            return Response({
                'message': f'Lead "{lead_name}" deleted successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class AgentsListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            agents = Employee.objects.select_related('user').all()
            
            agents_data = []
            for agent in agents:
                agent_dict = {
                    'id': agent.id,
                    'first_name': agent.user.first_name,
                    'last_name': agent.user.last_name,
                    'username': agent.user.username,
                    'full_name': f"{agent.user.first_name} {agent.user.last_name}".strip() or agent.user.username,
                }
                agents_data.append(agent_dict)
            
            return Response({
                'results': agents_data,
                'count': len(agents_data)
            })
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
