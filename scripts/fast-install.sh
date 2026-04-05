#!/bin/bash
# Fast node_modules restore — uses cached tarball instead of full pnpm install
# Reduces install from ~20min to ~1min on slow filesystems
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CACHE_TAR="/teamspace/studios/this_studio/.node_modules_cache.tar"
LOCKFILE="$PROJECT_DIR/pnpm-lock.yaml"
LOCKFILE_HASH_FILE="/teamspace/studios/this_studio/.node_modules_cache.lock_hash"

cd "$PROJECT_DIR"

# Check if node_modules already exists and is complete
if [ -f "node_modules/.modules.yaml" ]; then
    echo "✅ node_modules already present — running quick sync..."
    pnpm install --frozen-lockfile --prefer-offline 2>&1 | tail -3
    exit 0
fi

# Compute lockfile hash to detect staleness
CURRENT_HASH=$(md5sum "$LOCKFILE" | awk '{print $1}')
CACHED_HASH=""
[ -f "$LOCKFILE_HASH_FILE" ] && CACHED_HASH=$(cat "$LOCKFILE_HASH_FILE")

# Restore from cache if available and lockfile hasn't changed
if [ -f "$CACHE_TAR" ] && [ "$CURRENT_HASH" = "$CACHED_HASH" ]; then
    echo "⚡ Restoring node_modules from cache..."
    tar xf "$CACHE_TAR" 2>/dev/null || true
    echo "🔄 Running pnpm sync..."
    pnpm install --frozen-lockfile --prefer-offline 2>&1 | tail -3
    echo "✅ Done (restored from cache)"
    exit 0
fi

# Full install — cache miss or lockfile changed
echo "📦 Cache miss — running full pnpm install..."
pnpm install --frozen-lockfile --prefer-offline 2>&1
echo ""

# Save cache for next time
echo "💾 Saving node_modules cache (background)..."
DIRS_TO_TAR="node_modules"
[ -d "apps/frontend/node_modules" ] && DIRS_TO_TAR="$DIRS_TO_TAR apps/frontend/node_modules"
[ -d "apps/mobile/node_modules" ] && DIRS_TO_TAR="$DIRS_TO_TAR apps/mobile/node_modules"
[ -d "apps/desktop/node_modules" ] && DIRS_TO_TAR="$DIRS_TO_TAR apps/desktop/node_modules"
[ -d "packages/shared/node_modules" ] && DIRS_TO_TAR="$DIRS_TO_TAR packages/shared/node_modules"

tar cf "$CACHE_TAR" $DIRS_TO_TAR 2>/dev/null &
echo "$CURRENT_HASH" > "$LOCKFILE_HASH_FILE"
echo "✅ Install complete (cache building in background)"
