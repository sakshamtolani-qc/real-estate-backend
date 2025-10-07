from django.core.management.base import BaseCommand
from accounts.models import User, Employee

class Command(BaseCommand):
    help = 'Create dummy employees for admin dashboard demo.'

    def handle(self, *args, **options):
        dummy_data = [
            {'username': 'john', 'email': 'john@example.com', 'password': 'test1234', 'first_name': 'John', 'last_name': 'Doe', 'phone': '1234567890'},
            {'username': 'jane', 'email': 'jane@example.com', 'password': 'test1234', 'first_name': 'Jane', 'last_name': 'Smith', 'phone': '2345678901'},
            {'username': 'alice', 'email': 'alice@example.com', 'password': 'test1234', 'first_name': 'Alice', 'last_name': 'Brown', 'phone': '3456789012'},
            {'username': 'bob', 'email': 'bob@example.com', 'password': 'test1234', 'first_name': 'Bob', 'last_name': 'Johnson', 'phone': '4567890123'},
        ]
        for data in dummy_data:
            user, created = User.objects.get_or_create(username=data['username'], defaults={
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'phone': data['phone'],
                'is_employee': True,
            })
            if created:
                user.set_password(data['password'])
                user.save()
            Employee.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS('Dummy employees created.'))
