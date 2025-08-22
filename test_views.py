#!/usr/bin/env python
"""
Test script to verify views are working
"""

import os
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_classroom.settings')

import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

from attendance.views import attendance_list
from feedback.views import feedback_list

def test_views():
    """Test that views can be called without errors"""
    factory = RequestFactory()
    
    print("Testing attendance_list view...")
    try:
        request = factory.get('/attendance/')
        request.user = AnonymousUser()
        response = attendance_list(request)
        print(f"✅ attendance_list: Status {response.status_code}")
    except Exception as e:
        print(f"❌ attendance_list error: {e}")
    
    print("\nTesting feedback_list view...")
    try:
        request = factory.get('/feedback/')
        request.user = AnonymousUser()
        response = feedback_list(request)
        print(f"✅ feedback_list: Status {response.status_code}")
    except Exception as e:
        print(f"❌ feedback_list error: {e}")

if __name__ == '__main__':
    test_views()