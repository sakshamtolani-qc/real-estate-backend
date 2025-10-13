#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

# Import data from JSON file
print("Importing data from data_backup.json...")
call_command('loaddata', 'data_backup.json')
print("Data successfully imported to PostgreSQL database!")
