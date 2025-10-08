from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from leads.models import Lead, LeadSource
from accounts.models import Employee
import random


class Command(BaseCommand):
    help = 'Populate database with dummy leads'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating dummy leads...')
        
        # Get or create lead sources
        sources_data = [
            ('Website', 'Direct website inquiry'),
            ('Phone Call', 'Inbound phone inquiry'),
            ('Referral', 'Customer referral'),
            ('Social Media', 'Social media lead'),
            ('Walk-in', 'Direct walk-in customer'),
        ]
        
        sources = []
        for name, desc in sources_data:
            source, created = LeadSource.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            sources.append(source)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created lead source: {name}'))
        
        # Get all employees for assignment
        employees = list(Employee.objects.all())
        if not employees:
            self.stdout.write(self.style.WARNING('No employees found in database. Leads will be unassigned.'))
        
        # Dummy leads data
        dummy_leads = [
            {
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john.smith@example.com',
                'phone': '+1 (555) 123-4567',
                'budget_min': 150000,
                'budget_max': 250000,
                'status': 'new'
            },
            {
                'first_name': 'Emily',
                'last_name': 'Johnson',
                'email': 'emily.j@example.com',
                'phone': '+1 (555) 234-5678',
                'budget_min': 200000,
                'budget_max': 350000,
                'status': 'contacted'
            },
            {
                'first_name': 'Michael',
                'last_name': 'Williams',
                'email': 'michael.w@example.com',
                'phone': '+1 (555) 345-6789',
                'budget_min': 180000,
                'budget_max': 280000,
                'status': 'qualified'
            },
            {
                'first_name': 'Sarah',
                'last_name': 'Brown',
                'email': 'sarah.brown@example.com',
                'phone': '+1 (555) 456-7890',
                'budget_min': 220000,
                'budget_max': 320000,
                'status': 'proposal'
            },
            {
                'first_name': 'David',
                'last_name': 'Davis',
                'email': 'david.davis@example.com',
                'phone': '+1 (555) 567-8901',
                'budget_min': 300000,
                'budget_max': 450000,
                'status': 'negotiation'
            },
            {
                'first_name': 'Jessica',
                'last_name': 'Martinez',
                'email': 'jessica.m@example.com',
                'phone': '+1 (555) 678-9012',
                'budget_min': 175000,
                'budget_max': 275000,
                'status': 'won'
            },
            {
                'first_name': 'James',
                'last_name': 'Garcia',
                'email': 'james.garcia@example.com',
                'phone': '+1 (555) 789-0123',
                'budget_min': 140000,
                'budget_max': 200000,
                'status': 'new'
            },
            {
                'first_name': 'Lisa',
                'last_name': 'Rodriguez',
                'email': 'lisa.rodriguez@example.com',
                'phone': '+1 (555) 890-1234',
                'budget_min': 250000,
                'budget_max': 400000,
                'status': 'contacted'
            },
            {
                'first_name': 'Robert',
                'last_name': 'Wilson',
                'email': 'robert.w@example.com',
                'phone': '+1 (555) 901-2345',
                'budget_min': 190000,
                'budget_max': 290000,
                'status': 'qualified'
            },
            {
                'first_name': 'Jennifer',
                'last_name': 'Taylor',
                'email': 'jennifer.t@example.com',
                'phone': '+1 (555) 012-3456',
                'budget_min': 160000,
                'budget_max': 240000,
                'status': 'lost'
            },
            {
                'first_name': 'William',
                'last_name': 'Anderson',
                'email': 'william.a@example.com',
                'phone': '+1 (555) 111-2222',
                'budget_min': 280000,
                'budget_max': 380000,
                'status': 'proposal'
            },
            {
                'first_name': 'Amanda',
                'last_name': 'Thomas',
                'email': 'amanda.thomas@example.com',
                'phone': '+1 (555) 222-3333',
                'budget_min': 195000,
                'budget_max': 295000,
                'status': 'new'
            },
            {
                'first_name': 'Christopher',
                'last_name': 'Moore',
                'email': 'chris.moore@example.com',
                'phone': '+1 (555) 333-4444',
                'budget_min': 210000,
                'budget_max': 310000,
                'status': 'contacted'
            },
            {
                'first_name': 'Michelle',
                'last_name': 'Jackson',
                'email': 'michelle.j@example.com',
                'phone': '+1 (555) 444-5555',
                'budget_min': 170000,
                'budget_max': 270000,
                'status': 'qualified'
            },
            {
                'first_name': 'Daniel',
                'last_name': 'White',
                'email': 'daniel.white@example.com',
                'phone': '+1 (555) 555-6666',
                'budget_min': 320000,
                'budget_max': 480000,
                'status': 'negotiation'
            },
        ]
        
        # Create leads
        created_count = 0
        for lead_data in dummy_leads:
            # Check if lead already exists
            exists = Lead.objects.filter(
                email=lead_data['email']
            ).exists()
            
            if not exists:
                # Assign random source
                source = random.choice(sources)
                
                # Assign random employee if available
                assigned_to = random.choice(employees) if employees else None
                
                lead = Lead.objects.create(
                    first_name=lead_data['first_name'],
                    last_name=lead_data['last_name'],
                    email=lead_data['email'],
                    phone=lead_data['phone'],
                    budget_min=lead_data['budget_min'],
                    budget_max=lead_data['budget_max'],
                    status=lead_data['status'],
                    source=source,
                    assigned_to=assigned_to,
                )
                created_count += 1
                agent_name = f"{assigned_to.user.username}" if assigned_to else "Unassigned"
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created lead: {lead.full_name} (Status: {lead.status}, Agent: {agent_name})'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} leads!')
        )
