"""
Helper functions and signals for creating notifications
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Lead, Notification
from properties.models import Property
from accounts.models import User


def notify_admins_and_agents(notification_type, title, message, related_data=None, action_url=''):
    """
    Send notification to all admins and agents
    """
    # Get all admins and agents
    users = User.objects.filter(role__in=['admin', 'agent'])
    
    notifications = []
    for user in users:
        notification = Notification.objects.create(
            recipient=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_data=related_data or {},
            action_url=action_url
        )
        notifications.append(notification)
    
    return notifications


def notify_user(user_id, notification_type, title, message, related_data=None, action_url=''):
    """
    Send notification to a specific user
    """
    try:
        user = User.objects.get(id=user_id)
        notification = Notification.objects.create(
            recipient=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_data=related_data or {},
            action_url=action_url
        )
        return notification
    except User.DoesNotExist:
        return None


# Store previous assignment in memory before save
@receiver(pre_save, sender=Lead)
def store_previous_assignment(sender, instance, **kwargs):
    """
    Store the previous assignment before the lead is saved
    """
    if instance.pk:
        try:
            old_lead = Lead.objects.get(pk=instance.pk)
            instance._previous_assigned_to = old_lead.assigned_to
        except Lead.DoesNotExist:
            instance._previous_assigned_to = None
    else:
        instance._previous_assigned_to = None


# Signal: When a lead is created or assigned
@receiver(post_save, sender=Lead)
def lead_notification(sender, instance, created, **kwargs):
    """
    Send notifications for lead creation and assignment
    """
    # Notification for new lead creation
    if created:
        # Notify all admins and agents about new lead
        users = User.objects.filter(role__in=['admin', 'agent'])
        
        for user in users:
            Notification.objects.create(
                recipient=user,
                notification_type='customer_signup',
                title='New Lead Created',
                message=f'New lead: {instance.full_name} ({instance.email})',
                related_data={
                    'lead_id': instance.id,
                    'lead_name': instance.full_name,
                    'lead_email': instance.email,
                    'lead_phone': instance.phone,
                    'lead_source': instance.source.name if instance.source else 'Unknown'
                },
                action_url='/admin/leads' if user.role == 'admin' else '/agent/leads'
            )
    
    # Notification for lead assignment
    else:
        # Check if assignment changed
        previous_assigned = getattr(instance, '_previous_assigned_to', None)
        current_assigned = instance.assigned_to
        
        if current_assigned and previous_assigned != current_assigned:
            # Lead was newly assigned or reassigned
            agent_user = current_assigned.user
            
            Notification.objects.create(
                recipient=agent_user,
                notification_type='lead_assigned',
                title='New Lead Assigned to You',
                message=f'Lead {instance.full_name} has been assigned to you.',
                related_data={
                    'lead_id': instance.id,
                    'lead_name': instance.full_name,
                    'lead_email': instance.email,
                    'lead_phone': instance.phone,
                    'lead_status': instance.status
                },
                action_url='/agent/leads'
            )


# Signal: When a new property is added
# TODO: Add created_by field to Property model to enable this notification
# @receiver(post_save, sender=Property)
def property_added_notification(sender, instance, created, **kwargs):
    """
    Send notification to all agents/admins when a new property is added
    """
    if created:
        # Get the creator
        # DISABLED: Property model doesn't have created_by field yet
        return
        creator_role = instance.created_by.role if instance.created_by else None
        
        if creator_role == 'admin':
            # Notify all agents
            agents = User.objects.filter(role='agent')
            for agent in agents:
                Notification.objects.create(
                    recipient=agent,
                    notification_type='property_added',
                    title='New Property Added',
                    message=f'Admin added a new property: {instance.title}',
                    related_data={
                        'property_id': instance.id,
                        'property_title': instance.title,
                        'property_city': instance.city,
                        'property_type': instance.property_type
                    },
                    action_url=f'/properties/{instance.id}'
                )
        
        elif creator_role == 'agent':
            # Notify all admins
            admins = User.objects.filter(role='admin')
            for admin in admins:
                Notification.objects.create(
                    recipient=admin,
                    notification_type='property_added',
                    title='New Property Added by Agent',
                    message=f'{instance.created_by.get_full_name()} added a new property: {instance.title}',
                    related_data={
                        'property_id': instance.id,
                        'property_title': instance.title,
                        'property_city': instance.city,
                        'property_type': instance.property_type,
                        'added_by': instance.created_by.get_full_name()
                    },
                    action_url=f'/admin/properties/{instance.id}'
                )
