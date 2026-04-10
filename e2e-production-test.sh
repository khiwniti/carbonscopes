#!/bin/bash

################################################################################
# CarbonScope Production E2E Test Suite
# Tests Azure Static Web App + Container Apps Backend
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Production URLs
FRONTEND_URL="https://suna-frontend-app.azurewebsites.net"
BACKEND_URL="https://suna-backend-app.azurewebsites.net"

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNINGS=0

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_test() {
    echo -e "${CYAN}▶ Testing: $1${NC}"
    ((TOTAL_TESTS++))
}

print_success() {
    echo -e "${GREEN}  ✓ $1${NC}"
    ((PASSED_TESTS++))
}

print_error() {
    echo -e "${RED}  ✗ $1${NC}"
    ((FAILED_TESTS++))
}

print_warning() {
    echo -e "${YELLOW}  ⚠ $1${NC}"
    ((WARNINGS++))
}

print_info() {
    echo -e "${BLUE}  ℹ $1${NC}"
}

# Create test output directory
TEST_DIR="production-e2e-results-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$TEST_DIR"

clear
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║              CarbonScope Production E2E Test Suite                           ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${CYAN}Frontend:${NC} $FRONTEND_URL"
echo -e "${CYAN}Backend:${NC}  $BACKEND_URL"
echo -e "${CYAN}Results:${NC}  $TEST_DIR"
echo ""

# Test 1: Backend Health Check
print_header "Backend API Tests"

print_test "Backend health endpoint"
STATUS=$(timeout 10 curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/v1/health" 2>/dev/null || echo "000")
if [ "$STATUS" = "200" ]; then
    RESPONSE=$(timeout 10 curl -s "$BACKEND_URL/v1/health" 2>/dev/null || echo '{"error":"timeout"}')
    print_success "Health endpoint responding (200 OK)"
    echo "$RESPONSE" > "$TEST_DIR/backend-health.json"
    print_info "Response: $RESPONSE"
else
    print_error "Health endpoint failed (HTTP $STATUS)"
fi

print_test "Backend CORS headers"
CORS=$(timeout 10 curl -s -I "$BACKEND_URL/v1/health" 2>/dev/null | grep -i "access-control" || echo "")
if [ -n "$CORS" ]; then
    print_success "CORS headers present"
    echo "$CORS" > "$TEST_DIR/backend-cors.txt"
else
    print_warning "No CORS headers found"
fi

print_test "Backend response time"
START=$(date +%s%N)
timeout 10 curl -s -o /dev/null "$BACKEND_URL/v1/health" 2>/dev/null
END=$(date +%s%N)
RESPONSE_TIME=$(( ($END - $START) / 1000000 ))
if [ $RESPONSE_TIME -lt 2000 ]; then
    print_success "Response time: ${RESPONSE_TIME}ms (< 2s)"
else
    print_warning "Response time: ${RESPONSE_TIME}ms (slow)"
fi
echo "Response time: ${RESPONSE_TIME}ms" > "$TEST_DIR/backend-timing.txt"

# Test 2: Frontend Availability
print_header "Frontend Availability Tests"

print_test "Frontend homepage (200 OK)"
STATUS=$(timeout 10 curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo "000")
if [ "$STATUS" = "200" ]; then
    print_success "Homepage responding (200 OK)"
else
    print_error "Homepage failed (HTTP $STATUS)"
fi

print_test "Frontend HTML content"
HTML=$(timeout 10 curl -s "$FRONTEND_URL" 2>/dev/null || echo "")
if echo "$HTML" | grep -q "CarbonScope"; then
    print_success "CarbonScope branding found in HTML"
else
    print_warning "CarbonScope branding not found (might still be deploying)"
fi
echo "$HTML" > "$TEST_DIR/frontend-html.txt"

print_test "Frontend meta tags"
if echo "$HTML" | grep -q "charset"; then
    print_success "Meta charset present"
fi
if echo "$HTML" | grep -q "viewport"; then
    print_success "Viewport meta tag present"
fi

print_test "Frontend response time"
START=$(date +%s%N)
curl -s -o /dev/null "$FRONTEND_URL"
END=$(date +%s%N)
RESPONSE_TIME=$(( ($END - $START) / 1000000 ))
if [ $RESPONSE_TIME -lt 3000 ]; then
    print_success "Response time: ${RESPONSE_TIME}ms (< 3s)"
else
    print_warning "Response time: ${RESPONSE_TIME}ms (slow)"
fi
echo "Response time: ${RESPONSE_TIME}ms" > "$TEST_DIR/frontend-timing.txt"

# Test 3: SSL/TLS
print_header "SSL/TLS Security Tests"

print_test "Frontend SSL certificate"
if echo | openssl s_client -connect orange-river-0ce07e10f.6.azurestaticapps.net:443 -servername orange-river-0ce07e10f.6.azurestaticapps.net 2>/dev/null | grep -q "Verify return code: 0"; then
    print_success "Valid SSL certificate"
else
    print_warning "SSL certificate verification issue"
fi

print_test "Backend SSL certificate"
if echo | openssl s_client -connect carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io:443 -servername carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io 2>/dev/null | grep -q "Verify return code: 0"; then
    print_success "Valid SSL certificate"
else
    print_warning "SSL certificate verification issue"
fi

print_test "TLS version"
TLS_VERSION=$(echo | openssl s_client -connect orange-river-0ce07e10f.6.azurestaticapps.net:443 2>/dev/null | grep "Protocol" | awk '{print $3}')
if echo "$TLS_VERSION" | grep -q "TLSv1.2\|TLSv1.3"; then
    print_success "TLS version: $TLS_VERSION"
else
    print_warning "TLS version: $TLS_VERSION"
fi

# Test 4: Security Headers
print_header "Security Headers Tests"

print_test "Frontend security headers"
HEADERS=$(curl -s -I "$FRONTEND_URL")

if echo "$HEADERS" | grep -qi "x-frame-options\|content-security-policy"; then
    print_success "Security headers present"
else
    print_warning "Some security headers missing"
fi

if echo "$HEADERS" | grep -qi "strict-transport-security"; then
    print_success "HSTS enabled"
else
    print_warning "HSTS not found"
fi

echo "$HEADERS" > "$TEST_DIR/frontend-headers.txt"

# Test 5: Common Routes (if frontend is deployed)
print_header "Frontend Route Tests"

# Test key routes
ROUTES=(
    "/"
    "/about"
    "/pricing"
    "/auth"
)

for route in "${ROUTES[@]}"; do
    print_test "Route: $route"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL$route")
    if [ "$STATUS" = "200" ]; then
        print_success "Accessible (200 OK)"
    elif [ "$STATUS" = "404" ]; then
        print_warning "Not found (404) - might not be deployed yet"
    else
        print_error "Failed (HTTP $STATUS)"
    fi
done

# Test 6: API Endpoints
print_header "Backend API Endpoint Tests"

API_ENDPOINTS=(
    "/health"
    "/v1/health"
)

for endpoint in "${API_ENDPOINTS[@]}"; do
    print_test "Endpoint: $endpoint"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL$endpoint")
    if [ "$STATUS" = "200" ]; then
        print_success "Accessible (200 OK)"
    elif [ "$STATUS" = "404" ]; then
        print_warning "Not found (404)"
    else
        print_error "Failed (HTTP $STATUS)"
    fi
done

# Test 7: Performance
print_header "Performance Tests"

print_test "Frontend download size"
SIZE=$(curl -s "$FRONTEND_URL" | wc -c)
SIZE_KB=$((SIZE / 1024))
if [ $SIZE_KB -lt 500 ]; then
    print_success "HTML size: ${SIZE_KB}KB (< 500KB)"
else
    print_warning "HTML size: ${SIZE_KB}KB (large)"
fi
echo "HTML size: ${SIZE_KB}KB" > "$TEST_DIR/frontend-size.txt"

print_test "Backend uptime check"
for i in {1..3}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/v1/health")
    if [ "$STATUS" = "200" ]; then
        print_success "Health check #$i: OK"
    else
        print_error "Health check #$i: Failed"
    fi
    sleep 1
done

# Test 8: DNS Resolution
print_header "DNS Resolution Tests"

print_test "Frontend DNS resolution"
if dig +short orange-river-0ce07e10f.6.azurestaticapps.net | grep -q "[0-9]"; then
    IP=$(dig +short orange-river-0ce07e10f.6.azurestaticapps.net | head -1)
    print_success "Resolves to: $IP"
else
    print_error "DNS resolution failed"
fi

print_test "Backend DNS resolution"
if dig +short carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io | grep -q "[0-9]"; then
    IP=$(dig +short carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io | head -1)
    print_success "Resolves to: $IP"
else
    print_error "DNS resolution failed"
fi

# Test 9: Mobile Responsiveness (check viewport meta)
print_header "Mobile Responsiveness Tests"

print_test "Viewport meta tag"
if curl -s "$FRONTEND_URL" | grep -q 'name="viewport"'; then
    VIEWPORT=$(curl -s "$FRONTEND_URL" | grep -o 'content="[^"]*"' | head -1)
    print_success "Viewport meta tag found: $VIEWPORT"
else
    print_warning "Viewport meta tag not found"
fi

# Generate Summary Report
print_header "Test Summary Report"

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                          TEST RESULTS SUMMARY                                ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${CYAN}Total Tests:${NC}    $TOTAL_TESTS"
echo -e "${GREEN}Passed:${NC}        $PASSED_TESTS"
echo -e "${RED}Failed:${NC}        $FAILED_TESTS"
echo -e "${YELLOW}Warnings:${NC}      $WARNINGS"
echo ""

# Calculate success rate
SUCCESS_RATE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
echo -e "${CYAN}Success Rate:${NC}  ${SUCCESS_RATE}%"
echo ""

# Overall status
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    OVERALL_STATUS="PASS"
elif [ $SUCCESS_RATE -ge 70 ]; then
    echo -e "${YELLOW}⚠ TESTS PASSED WITH WARNINGS${NC}"
    OVERALL_STATUS="PASS_WITH_WARNINGS"
else
    echo -e "${RED}✗ TESTS FAILED${NC}"
    OVERALL_STATUS="FAIL"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Production URLs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL"
echo ""
echo "Test Results: $TEST_DIR"
echo ""

# Generate JSON report
cat > "$TEST_DIR/test-report.json" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "frontend_url": "$FRONTEND_URL",
  "backend_url": "$BACKEND_URL",
  "total_tests": $TOTAL_TESTS,
  "passed": $PASSED_TESTS,
  "failed": $FAILED_TESTS,
  "warnings": $WARNINGS,
  "success_rate": $SUCCESS_RATE,
  "overall_status": "$OVERALL_STATUS"
}
EOF

# Generate Markdown report
cat > "$TEST_DIR/README.md" << EOF
# CarbonScope Production E2E Test Report

**Date:** $(date)  
**Status:** $OVERALL_STATUS  

## Summary

- **Total Tests:** $TOTAL_TESTS
- **Passed:** $PASSED_TESTS ✓
- **Failed:** $FAILED_TESTS ✗
- **Warnings:** $WARNINGS ⚠
- **Success Rate:** ${SUCCESS_RATE}%

## Production URLs

- **Frontend:** $FRONTEND_URL
- **Backend:** $BACKEND_URL

## Test Categories

1. Backend API Tests
2. Frontend Availability Tests
3. SSL/TLS Security Tests
4. Security Headers Tests
5. Frontend Route Tests
6. Backend API Endpoint Tests
7. Performance Tests
8. DNS Resolution Tests
9. Mobile Responsiveness Tests

## Files Generated

- \`test-report.json\` - JSON test results
- \`backend-health.json\` - Backend health response
- \`frontend-html.txt\` - Frontend HTML
- \`frontend-headers.txt\` - HTTP headers
- \`backend-timing.txt\` - Response times

## Next Steps

$(if [ "$OVERALL_STATUS" = "PASS" ]; then
    echo "✅ All tests passed! Production deployment is healthy."
elif [ "$OVERALL_STATUS" = "PASS_WITH_WARNINGS" ]; then
    echo "⚠️ Most tests passed but some warnings detected. Review warnings above."
else
    echo "❌ Some tests failed. Review failed tests and fix issues before going live."
fi)

---
Generated by CarbonScope E2E Test Suite
EOF

print_success "Test report saved to: $TEST_DIR/README.md"

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║  View full report: cat $TEST_DIR/README.md"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Exit with appropriate code
if [ "$OVERALL_STATUS" = "FAIL" ]; then
    exit 1
else
    exit 0
fi
