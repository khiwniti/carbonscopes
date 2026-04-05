#!/usr/bin/env python3
"""
Test script for rate limiting on authentication endpoints.

This script tests:
1. /auth/send-otp endpoint (should be rate limited to 5 requests per 15 minutes)
2. /api/api-keys endpoint (should be rate limited to 5 requests per 15 minutes)
3. Proper 429 response with retry-after information

Usage:
    python test_rate_limit.py
"""

import asyncio
import httpx
import sys
import os
from datetime import datetime


# Base URL for the API (adjust as needed)
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/v1")

# Test email for OTP endpoint
TEST_EMAIL = "test@example.com"


async def test_auth_endpoint_rate_limit():
    """Test rate limiting on /auth/send-otp endpoint."""
    print(f"\n{'='*60}")
    print("Testing Rate Limit on /auth/send-otp endpoint")
    print(f"{'='*60}\n")

    endpoint = f"{BASE_URL}/auth/send-otp"
    print(f"Endpoint: {endpoint}")
    print(f"Rate limit: 5 requests per 15 minutes\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        successful_requests = 0
        rate_limited = False

        for i in range(7):  # Try 7 requests (should hit limit at 6th)
            print(f"Request #{i+1} at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}...", end=" ")

            try:
                response = await client.post(
                    endpoint,
                    json={"email": TEST_EMAIL},
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 429:
                    rate_limited = True
                    print(f"❌ RATE LIMITED (429)")
                    print(f"   Response: {response.json()}")

                    # Check for retry-after header
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        print(f"   ✅ Retry-After header present: {retry_after} seconds")
                    else:
                        print(f"   ⚠️  Retry-After header missing!")

                    # Check response format
                    data = response.json()
                    if "error" in data and "retry_after" in data:
                        print(f"   ✅ Proper error format with retry_after")
                    else:
                        print(f"   ⚠️  Response missing expected fields")
                    break

                elif response.status_code in (200, 404, 500):
                    # 404/500 are OK - they mean the endpoint processed but email doesn't exist
                    # We just care about rate limiting behavior
                    successful_requests += 1
                    print(f"✅ SUCCESS (status: {response.status_code})")

                else:
                    print(f"⚠️  Unexpected status: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")

            except Exception as e:
                print(f"❌ ERROR: {str(e)}")

            # Small delay between requests
            await asyncio.sleep(0.2)

    print(f"\nResult:")
    print(f"  Successful requests before rate limit: {successful_requests}")
    print(f"  Rate limit triggered: {'✅ YES' if rate_limited else '❌ NO'}")

    if rate_limited and successful_requests >= 5:
        print(f"\n✅ PASS: Rate limiting works correctly!")
        return True
    else:
        print(f"\n❌ FAIL: Rate limiting not working as expected")
        return False


async def test_api_keys_endpoint_rate_limit():
    """Test rate limiting on /api/api-keys endpoint."""
    print(f"\n{'='*60}")
    print("Testing Rate Limit on /api/api-keys endpoint")
    print(f"{'='*60}\n")

    endpoint = f"{BASE_URL}/api-keys"
    print(f"Endpoint: {endpoint}")
    print(f"Rate limit: 5 requests per 15 minutes")
    print(f"Note: This endpoint requires authentication, so we expect 401 errors\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        successful_requests = 0
        rate_limited = False

        for i in range(7):  # Try 7 requests
            print(f"Request #{i+1} at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}...", end=" ")

            try:
                response = await client.post(
                    endpoint,
                    json={"title": "Test Key", "description": "Test"},
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 429:
                    rate_limited = True
                    print(f"❌ RATE LIMITED (429)")
                    print(f"   Response: {response.json()}")

                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        print(f"   ✅ Retry-After header present: {retry_after} seconds")

                    break

                elif response.status_code in (401, 403):
                    # Auth errors are expected - we're testing rate limiting, not auth
                    successful_requests += 1
                    print(f"✅ PROCESSED (status: {response.status_code} - auth required)")

                else:
                    print(f"⚠️  Status: {response.status_code}")

            except Exception as e:
                print(f"❌ ERROR: {str(e)}")

            await asyncio.sleep(0.2)

    print(f"\nResult:")
    print(f"  Requests processed before rate limit: {successful_requests}")
    print(f"  Rate limit triggered: {'✅ YES' if rate_limited else '❌ NO'}")

    if rate_limited and successful_requests >= 5:
        print(f"\n✅ PASS: Rate limiting works correctly!")
        return True
    else:
        print(f"\n❌ FAIL: Rate limiting not working as expected")
        return False


async def main():
    """Run all rate limit tests."""
    print("\n" + "="*60)
    print("RATE LIMITING TEST SUITE")
    print("="*60)
    print(f"API Base URL: {BASE_URL}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check if server is running
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL.rsplit('/v1', 1)[0]}/health")
            if response.status_code == 200:
                print(f"✅ Server is running")
            else:
                print(f"⚠️  Server responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print(f"\nPlease ensure the API server is running at {BASE_URL}")
        sys.exit(1)

    # Run tests
    results = []

    # Test 1: Auth endpoint
    result1 = await test_auth_endpoint_rate_limit()
    results.append(("Auth endpoint (/auth/send-otp)", result1))

    # Wait a bit before next test to avoid cross-contamination
    print(f"\nWaiting 2 seconds before next test...")
    await asyncio.sleep(2)

    # Test 2: API Keys endpoint
    result2 = await test_api_keys_endpoint_rate_limit()
    results.append(("API Keys endpoint (/api-keys)", result2))

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}\n")

    all_passed = all(result for _, result in results)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print(f"{'='*60}\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
