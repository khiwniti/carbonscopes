# CarbonScopes Makefile
# Easy commands for development and deployment

.PHONY: help install dev backend frontend test clean build deploy

# Default target
help:
@echo "CarbonScopes - Available Commands"
@echo ""
@echo "  make install      - Install all dependencies (root, backend, frontend)"
@echo "  make dev          - Start development servers (backend + frontend)"
@echo "  make backend      - Start backend only (port 8000)"
@echo "  make frontend     - Start frontend only (port 3000)"
@echo "  make build        - Build for production"
@echo "  make deploy       - Deploy to Cloudflare Workers"
@echo "  make clean        - Clean build artifacts"
@echo "  make test         - Run tests"
@echo ""

# Install all dependencies
install:
@echo "📦 Installing dependencies..."
@pnpm install

# Development - run both backend and frontend
dev:
@echo "🚀 Starting development servers..."
@pnpm dev

# Backend only
backend:
@echo "⚡ Starting backend server..."
@cd apps/backend && pnpm dev

# Frontend only
frontend:
@echo "🎨 Starting frontend server..."
@cd apps/frontend && pnpm dev

# Build for production
build:
@echo "🔨 Building for production..."
@pnpm build

# Build frontend specifically
build-frontend:
@echo "🔨 Building frontend..."
@cd apps/frontend && pnpm build

# Build backend specifically
build-backend:
@echo "🔨 Building backend..."
@cd apps/backend && pnpm build

# Deploy to Cloudflare Workers
deploy:
@echo "☁️ Deploying to Cloudflare Workers..."
@cd apps/frontend && pnpm build && npx wrangler deploy

# Clean build artifacts
clean:
@echo "🧹 Cleaning build artifacts..."
@rm -rf apps/frontend/.next
@rm -rf apps/frontend/.vercel
@rm -rf apps/frontend/.output
@rm -rf apps/frontend/.cloudflare-pages
@rm -rf apps/backend/dist
@rm -rf node_modules/.cache
@echo "✅ Clean complete"

# Run tests
test:
@echo "🧪 Running tests..."
@pnpm test

# Frontend tests
test-frontend:
@echo "🧪 Running frontend tests..."
@cd apps/frontend && pnpm test

# Backend tests
test-backend:
@echo "🧪 Running backend tests..."
@cd apps/backend && pnpm test

# Lint code
lint:
@echo "🔍 Linting code..."
@pnpm lint

# Format code
format:
@echo "✨ Formatting code..."
@pnpm format

# Docker commands
docker-build:
@echo "🐳 Building Docker images..."
@docker build -t carbonscopes-backend -f apps/backend/Dockerfile apps/backend
@docker build -t carbonscopes-frontend -f apps/frontend/Dockerfile apps/frontend

docker-up:
@echo "🐳 Starting Docker containers..."
@docker-compose up -d

docker-down:
@echo "🐳 Stopping Docker containers..."
@docker-compose down

# Database commands
db-migrate:
@echo "📊 Running database migrations..."
@cd apps/backend && pnpm db:migrate

db-seed:
@echo "🌱 Seeding database..."
@cd apps/backend && pnpm db:seed

db-reset:
@echo "🔄 Resetting database..."
@cd apps/backend && pnpm db:reset

# Cloudflare deployment
cf-setup:
@echo "☁️ Setting up Cloudflare..."
@cd apps/frontend && npx wrangler init

cf-deploy:
@echo "☁️ Deploying to Cloudflare Workers..."
@cd apps/frontend && pnpm build && npx wrangler deploy

cf-dev:
@echo "☁️ Starting Cloudflare development..."
@cd apps/frontend && npx wrangler dev

# Vercel deployment
vercel-deploy:
@echo "▲ Deploying to Vercel..."
@cd apps/frontend && pnpm build && npx vercel --prod
