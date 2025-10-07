from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create a predefined admin user for testing"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        user, created = User.objects.get_or_create(username="admin")
        user.email = "admin@example.com"
        user.is_superuser = True
        user.is_staff = True
        user.set_password("admin123")
        user.save()
        self.stdout.write(self.style.SUCCESS("Admin user set to: admin@example.com / admin123"))