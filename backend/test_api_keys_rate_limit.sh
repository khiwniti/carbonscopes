#!/bin/bash

# Test rate limiting on /api/api-keys endpoint
# Should allow 5 requests, then block with 429

BACKEND_URL="${BACKEND_URL:-http://localhost:3000}"
ENDPOINT="$BACKEND_URL/api/api-keys"

# Need a valid JWT token for this endpoint
if [ -z "$TEST_JWT_TOKEN" ]; then
  echo "Error: TEST_JWT_TOKEN environment variable not set"
  echo "Please set a valid JWT token: export TEST_JWT_TOKEN='your-token'"
  exit 1
fi

echo "Testing rate limit on $ENDPOINT"
echo "Expected: First 5 requests succeed, 6th request returns 429"
echo ""

for i in {1..6}; do
  echo "Request $i:"
  response=$(curl -s -w "\nHTTP_CODE:%{http_code}\n" -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TEST_JWT_TOKEN" \
    -d '{"title": "Test Key '"$i"'", "description": "Test", "expires_in_days": 30}' 2>&1)
  
  http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
  body=$(echo "$response" | grep -v "HTTP_CODE:")
  
  echo "Status: $http_code"
  
  if [ "$http_code" == "429" ]; then
    echo "✓ Rate limit triggered!"
    retry_after=$(echo "$body" | grep -o '"retry_after":"[^"]*"' | cut -d'"' -f4)
    echo "Retry after: $retry_after"
    break
  else
    echo "Response preview: ${body:0:100}..."
  fi
  
  echo ""
  sleep 1
done

echo "Test complete."
