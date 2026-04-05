#!/usr/bin/env bash
# fast-check.sh — Quick validation without full Next.js build (~15-30s)
# Usage:  bash fast-check.sh [--fix]

cd "$(dirname "$0")"

FIX=${1:-""}
PASS=0
FAIL=0

ok()  { echo "  ✅ $1"; PASS=$((PASS+1)); }
err() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }

echo ""
echo "⚡ Fast Check — $(date '+%H:%M:%S')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 1. TypeScript (incremental — reuses .tsbuildinfo) ───────────────────────
echo ""
echo "1️⃣  TypeScript"
TS_OUT=$(bunx tsc --noEmit --skipLibCheck --incremental 2>&1 || true)
TS_ERRORS=$(echo "$TS_OUT" | grep "error TS" | \
  grep -v "TS1005\|TS1109\|TS1128\|TS1131\|TS1381\|TS1011\|TS1382\|TS1134\|TS2809" | \
  wc -l)
if [ "$TS_ERRORS" -eq 0 ]; then
  ok "No new TypeScript errors"
else
  err "$TS_ERRORS TypeScript error(s)"
  echo "$TS_OUT" | grep "error TS" | \
    grep -v "TS1005\|TS1109\|TS1128\|TS1131\|TS1381\|TS1011\|TS1382\|TS1134\|TS2809" | head -5
fi

# ── 2. Console.log check (instant) ──────────────────────────────────────────
echo ""
echo "2️⃣  No bare console.log"
CONSOLE_COUNT=$(grep -rn "console\.\(log\|warn\|info\|debug\)" \
  src/ --include="*.tsx" --include="*.ts" 2>/dev/null | \
  grep -v "logger\.ts\|//.*console\|eslint-disable\|__tests__\|\.test\.\|\.spec\." | wc -l)
if [ "$CONSOLE_COUNT" -eq 0 ]; then
  ok "No bare console.log/warn/info/debug"
else
  err "$CONSOLE_COUNT bare console statements (use logger)"
fi

# ── 3. XSS sanitization (instant) ───────────────────────────────────────────
echo ""
echo "3️⃣  XSS sanitization"
UNSAFE=$(grep -rn "dangerouslySetInnerHTML" src/ --include="*.tsx" 2>/dev/null | \
  grep -v "getSafeHtml\|sanitize\|DOMPurify" | \
  grep -v "__html: \`\|__html: JSON\.stringify\|style dangerouslySet" | wc -l)
if [ "$UNSAFE" -eq 0 ]; then
  ok "All dynamic dangerouslySetInnerHTML uses sanitized"
else
  err "$UNSAFE potentially unsanitized dangerouslySetInnerHTML"
  grep -rn "dangerouslySetInnerHTML" src/ --include="*.tsx" | \
    grep -v "getSafeHtml\|sanitize\|DOMPurify\|__html: \`\|__html: JSON\.stringify\|style dangerouslySet" | head -3
fi

# ── 4. Import casing (instant) ───────────────────────────────────────────────
echo ""
echo "4️⃣  Import casing (no kortix-/CarbonScope-)"
BAD=$(grep -rn "CarbonScope-\|kortix-" src/ --include="*.tsx" --include="*.ts" 2>/dev/null | \
  grep "from\|import" | wc -l)
if [ "$BAD" -eq 0 ]; then
  ok "No wrong-cased imports"
else
  err "$BAD wrong-cased imports"
  grep -rn "CarbonScope-\|kortix-" src/ --include="*.tsx" --include="*.ts" | \
    grep "from\|import" | head -3
fi

# ── 5. Security check (instant) ──────────────────────────────────────────────
echo ""
echo "5️⃣  Security"
ENV_LEAKS=$(grep -rn "console\.\(log\|info\).*process\.env" src/ \
  --include="*.tsx" --include="*.ts" 2>/dev/null | wc -l)
if [ "$ENV_LEAKS" -eq 0 ]; then
  ok "No env var logging"
else
  err "$ENV_LEAKS env var logging found"
fi

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TOTAL=$((PASS+FAIL))
if [ "$FAIL" -eq 0 ]; then
  echo "✅ All $TOTAL checks passed"
  exit 0
else
  echo "❌ $FAIL/$TOTAL checks failed"
  exit 1
fi
