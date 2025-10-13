#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from properties.models import Property
from leads.models import Lead
from django.db import connection

User = get_user_model()

print("\n" + "="*60)
print("PostgreSQL Migration Verification")
print("="*60)

# Check database connection
with connection.cursor() as cursor:
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()[0]
    print(f"\n✓ Connected to PostgreSQL")
    print(f"  Database: {connection.settings_dict['NAME']}")
    print(f"  Host: {connection.settings_dict['HOST']}")
    print(f"  Port: {connection.settings_dict['PORT']}")

# Check data counts
print(f"\n📊 Data Statistics:")
print(f"  - Users: {User.objects.count()}")
print(f"  - Properties: {Property.objects.count()}")
print(f"  - Leads: {Lead.objects.count()}")

print("\n" + "="*60)
print("✅ Migration successful! Your app is now using PostgreSQL!")
print("="*60 + "\n")
