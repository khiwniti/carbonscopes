#!/bin/bash

# Test script for dev authentication bypass
# This script tests both bypass methods without requiring the backend to be running

echo "🧪 Dev Authentication Bypass Test Script"
echo "=========================================="
echo ""

# Check if .env has DEV_AUTH_BYPASS=true
echo "📝 Checking .env configuration..."
if grep -q "^DEV_AUTH_BYPASS=true" .env 2>/dev/null; then
    echo "✅ DEV_AUTH_BYPASS=true found in .env"
else
    echo "❌ DEV_AUTH_BYPASS=true not found in .env"
    exit 1
fi

if grep -q "^DEV_TEST_USER_ID=00000000-0000-0000-0000-000000000001" .env 2>/dev/null; then
    echo "✅ DEV_TEST_USER_ID configured in .env"
else
    echo "❌ DEV_TEST_USER_ID not found in .env"
    exit 1
fi

if grep -q "^DEV_TEST_EMAIL=test@dev.local" .env 2>/dev/null; then
    echo "✅ DEV_TEST_EMAIL configured in .env"
else
    echo "❌ DEV_TEST_EMAIL not found in .env"
    exit 1
fi

echo ""
echo "📋 Checking implementation in auth_utils.py..."

# Check for bypass implementation
if grep -q "DEV_AUTH_BYPASS" core/utils/auth_utils.py 2>/dev/null; then
    echo "✅ DEV_AUTH_BYPASS implementation found"

    # Show the bypass code
    echo ""
    echo "🔍 Bypass implementation (lines 399-424):"
    sed -n '399,424p' core/utils/auth_utils.py | head -26
else
    echo "❌ DEV_AUTH_BYPASS implementation not found"
    exit 1
fi

echo ""
echo "📚 Checking DEV_README.md documentation..."
if [ -f "DEV_README.md" ]; then
    echo "✅ DEV_README.md exists"
    echo ""
    echo "📄 Documentation preview:"
    head -20 DEV_README.md
else
    echo "❌ DEV_README.md not found"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ All checks passed!"
echo ""
echo "📖 To test with a running backend:"
echo ""
echo "Method 1 - Using x-dev-test-user header:"
echo "  curl -X GET http://localhost:8000/api/v1/threads \\"
echo "    -H 'x-dev-test-user: true'"
echo ""
echo "Method 2 - Using Bearer token:"
echo "  curl -X GET http://localhost:8000/api/v1/threads \\"
echo "    -H 'Authorization: Bearer dev:test@dev.local'"
echo ""
echo "🚀 To start the backend:"
echo "  cd suna-init/backend && uvicorn main:app --reload"
