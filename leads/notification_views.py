from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Notification
from accounts.models import User
import logging

logger = logging.getLogger(__name__)


class NotificationListAPIView(APIView):
    """Get all notifications for the current user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            
            # Get query parameters
            unread_only = request.query_params.get('unread_only', 'false').lower() == 'true'
            limit = int(request.query_params.get('limit', 50))
            
            # Build query
            notifications = Notification.objects.filter(recipient=user)
            
            if unread_only:
                notifications = notifications.filter(is_read=False)
            
            notifications = notifications[:limit]
            
            # Serialize data
            notifications_data = []
            for notif in notifications:
                notifications_data.append({
                    'id': notif.id,
                    'type': notif.notification_type,
                    'title': notif.title,
                    'message': notif.message,
                    'is_read': notif.is_read,
                    'related_data': notif.related_data,
                    'action_url': notif.action_url,
                    'created_at': notif.created_at.isoformat(),
                    'read_at': notif.read_at.isoformat() if notif.read_at else None,
                })
            
            unread_count = Notification.objects.filter(recipient=user, is_read=False).count()
            
            logger.info(f'User {user.email} fetched {len(notifications_data)} notifications')
            
            return Response({
                'notifications': notifications_data,
                'unread_count': unread_count,
                'total_count': len(notifications_data)
            })
        except Exception as e:
            logger.error(f'Error fetching notifications for user {request.user.email}: {str(e)}')
            return Response({
                'notifications': [],
                'unread_count': 0,
                'total_count': 0,
                'error': 'Failed to fetch notifications'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationMarkReadAPIView(APIView):
    """Mark notification(s) as read"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        notification_ids = request.data.get('notification_ids', [])
        
        if not notification_ids:
            return Response({
                'message': 'No notification IDs provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark notifications as read
        notifications = Notification.objects.filter(
            id__in=notification_ids,
            recipient=user,
            is_read=False
        )
        
        count = notifications.update(is_read=True, read_at=timezone.now())
        
        return Response({
            'message': f'{count} notification(s) marked as read',
            'count': count
        })


class NotificationMarkAllReadAPIView(APIView):
    """Mark all notifications as read for current user"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        count = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({
            'message': f'{count} notification(s) marked as read',
            'count': count
        })


class NotificationDeleteAPIView(APIView):
    """Delete a notification"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, notification_id):
        user = request.user
        
        notification = get_object_or_404(Notification, id=notification_id, recipient=user)
        notification.delete()
        
        return Response({
            'message': 'Notification deleted successfully'
        })


class NotificationCreateAPIView(APIView):
    """Create a new notification (for internal use or admin)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data
        
        # Get recipient
        recipient_id = data.get('recipient_id')
        if not recipient_id:
            return Response({
                'message': 'Recipient ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response({
                'message': 'Recipient not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create notification
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=data.get('type', 'general'),
            title=data.get('title', 'New Notification'),
            message=data.get('message', ''),
            related_data=data.get('related_data', {}),
            action_url=data.get('action_url', '')
        )
        
        return Response({
            'message': 'Notification created successfully',
            'notification_id': notification.id
        }, status=status.HTTP_201_CREATED)


def create_notification_for_users(user_ids, notification_type, title, message, related_data=None, action_url=''):
    """
    Helper function to create notifications for multiple users
    Can be called from other views or signals
    """
    notifications = []
    for user_id in user_ids:
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
            notifications.append(notification)
        except User.DoesNotExist:
            continue
    
    return notifications
