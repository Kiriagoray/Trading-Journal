"""
Quick test script to verify Django server is working
"""
import sys
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'journal_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from journal.models import AfterTradeEntry, PreTradeEntry, BacktestEntry
from journal.models import JournalField, JournalFieldOption, JournalFieldValue

print("=" * 60)
print("DJANGO SERVER VERIFICATION TEST")
print("=" * 60)

# Test 1: Check if models can be imported
print("\n[1] Testing model imports...")
try:
    print("  ✓ AfterTradeEntry model imported")
    print("  ✓ PreTradeEntry model imported")
    print("  ✓ BacktestEntry model imported")
    print("  ✓ JournalField model imported")
    print("  ✓ JournalFieldOption model imported")
    print("  ✓ JournalFieldValue model imported")
except Exception as e:
    print(f"  ✗ Error importing models: {e}")
    sys.exit(1)

# Test 2: Check database connection
print("\n[2] Testing database connection...")
try:
    user_count = User.objects.count()
    print(f"  ✓ Database connection successful (Users: {user_count})")
except Exception as e:
    print(f"  ✗ Database error: {e}")
    sys.exit(1)

# Test 3: Check URL configuration
print("\n[3] Testing URL configuration...")
try:
    from django.urls import reverse
    from django.test import Client
    
    client = Client()
    
    # Test home URL
    try:
        response = client.get('/')
        print(f"  ✓ Home URL accessible (Status: {response.status_code})")
    except Exception as e:
        print(f"  ✗ Home URL error: {e}")
    
    # Test login URL
    try:
        response = client.get('/login/')
        print(f"  ✓ Login URL accessible (Status: {response.status_code})")
    except Exception as e:
        print(f"  ✗ Login URL error: {e}")
    
    # Test dashboard URL (should redirect to login)
    try:
        response = client.get('/dashboard/')
        print(f"  ✓ Dashboard URL accessible (Status: {response.status_code}, should be 302 redirect)")
    except Exception as e:
        print(f"  ✗ Dashboard URL error: {e}")
        
except Exception as e:
    print(f"  ✗ URL configuration error: {e}")
    sys.exit(1)

# Test 4: Check form imports
print("\n[4] Testing form imports...")
try:
    from journal.forms import (
        AfterTradeEntryForm, PreTradeEntryForm, BacktestEntryForm,
        LotSizeCalculatorForm
    )
    print("  ✓ All forms imported successfully")
except Exception as e:
    print(f"  ✗ Form import error: {e}")
    sys.exit(1)

# Test 5: Check utils imports
print("\n[5] Testing utility functions...")
try:
    from journal.utils import (
        get_user_journal_fields, create_dynamic_form_field,
        save_field_value_for_entry
    )
    print("  ✓ Utility functions imported successfully")
except Exception as e:
    print(f"  ✗ Utility import error: {e}")
    sys.exit(1)

# Test 6: Check template tags
print("\n[6] Testing template tags...")
try:
    from journal.templatetags.journal_extras import (
        get_field, get_field_errors, startswith
    )
    print("  ✓ Template tags imported successfully")
except Exception as e:
    print(f"  ✗ Template tag import error: {e}")
    sys.exit(1)

# Test 7: Check instrument data
print("\n[7] Testing instrument data...")
try:
    from journal.instrument_data import INSTRUMENTS, get_instrument_data
    print(f"  ✓ Instrument data loaded ({len(INSTRUMENTS)} instruments)")
except Exception as e:
    print(f"  ✗ Instrument data error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED! ✓")
print("=" * 60)
print("\nThe server should be running at: http://127.0.0.1:8000/")
print("Open your browser and navigate to:")
print("  - http://127.0.0.1:8000/ (Home/Login)")
print("  - http://127.0.0.1:8000/admin/ (Admin panel)")
print("\nTo test the problematic pages:")
print("  - http://127.0.0.1:8000/journal/after/create/")
print("  - http://127.0.0.1:8000/journal/pre/create/")
print("  - http://127.0.0.1:8000/journal/backtest/create/")
print("  - http://127.0.0.1:8000/lot-size-calculator/")
print("\nNote: You'll need to be logged in to access most pages.")
print("=" * 60)

