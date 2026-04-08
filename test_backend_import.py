#!/usr/bin/env python
"""
Quick test to verify the backend api.py can be imported without errors.
This helps identify import issues and startup problems early.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

print("=" * 60)
print("🔍 Testing Backend Import")
print("=" * 60)

try:
    print("\n1️⃣  Importing api module...")
    import api
    print("✅ api module imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n2️⃣  Checking FastAPI app...")
    assert hasattr(api, 'app'), "api.app not found"
    print(f"✅ FastAPI app found: {api.app}")
except Exception as e:
    print(f"❌ App check failed: {e}")
    sys.exit(1)

try:
    print("\n3️⃣  Checking routers...")
    # Check that api_router was created
    assert hasattr(api, 'api_router'), "api_router not found"
    print(f"✅ API router found: {api.api_router}")
except Exception as e:
    print(f"❌ Router check failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! Backend appears to be working.")
print("=" * 60)
