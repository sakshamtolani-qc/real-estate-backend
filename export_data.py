#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

# Export data to JSON file with UTF-8 encoding
with open('data_backup.json', 'w', encoding='utf-8') as f:
    call_command(
        'dumpdata',
        exclude=['auth.permission', 'contenttypes'],
        indent=2,
        stdout=f
    )

print("Data successfully exported to data_backup.json")
