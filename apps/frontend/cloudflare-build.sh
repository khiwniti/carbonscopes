#!/bin/bash
# Cloudflare Pages build script for CarbonScope frontend
# This script handles workspace dependencies before the main build

set -e

echo "Starting Cloudflare Pages build..."

# Step 1: Install shared package dependencies
cd packages/shared
pnpm install --frozen-lockfile
cd ../..

# Step 2: Create symlink or copy shared package to frontend node_modules
mkdir -p apps/frontend/node_modules/@agentpress
cp -r packages/shared apps/frontend/node_modules/@agentpress/

# Step 3: Install frontend dependencies
cd apps/frontend
pnpm install --frozen-lockfile

# Step 4: Build the frontend
pnpm build

echo "Build complete!"