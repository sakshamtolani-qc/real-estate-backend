from django.core.management.base import BaseCommand
from accounts.models import User, Employee

MOCK_EMPLOYEES = [
    {"name": "Lorem Ipsum", "phone": "09203XXXX", "leads": 20, "offersMade": 20, "status": "Active"},
    {"name": "Lorem Ipsum", "phone": "09203XXXX", "leads": 30, "offersMade": 30, "status": "Active"},
    {"name": "Lorem Ipsum", "phone": "09203XXXX", "leads": 40, "offersMade": 40, "status": "InActive"},
    {"name": "Lorem Ipsum", "phone": "09203XXXX", "leads": 25, "offersMade": 25, "status": "Active"},
    {"name": "Lorem Ipsum", "phone": "09203XXXX", "leads": 19, "offersMade": 19, "status": "InActive"},
    {"name": "Lorem Ipsum", "phone": "09203XXXX", "leads": 4, "offersMade": 4, "status": "Active"},
    {"name": "Lorem Ipsum", "phone": "09203XXXX", "leads": 10, "offersMade": 10, "status": "InActive"},
    {"name": "Lorem Ipsum", "phone": "09203XXXX", "leads": 6, "offersMade": 6, "status": "Active"},
    {"name": "Lorem Ipsum", "phone": "09203XXXX", "leads": 7, "offersMade": 7, "status": "InActive"},
]

class Command(BaseCommand):
    help = "Populate mock employees"

    def handle(self, *args, **kwargs):
        for idx, emp in enumerate(MOCK_EMPLOYEES, start=1):
            username = f"employee{idx}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "phone": emp["phone"],
                    "is_employee": True,
                    "first_name": emp["name"],
                }
            )
            Employee.objects.get_or_create(
                user=user,
                defaults={
                    "status": emp["status"]
                }
            )
        self.stdout.write(self.style.SUCCESS("Mock employees populated."))
