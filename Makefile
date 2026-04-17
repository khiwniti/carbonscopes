# CarbonScopes Makefile
.PHONY: help install start dev frontend build deploy clean test lint

help:
	@echo "CarbonScopes - Available Commands:"
	@echo "  make install    - Install all dependencies"
	@echo "  make start      - Start all development servers"
	@echo "  make frontend   - Start frontend only (port 3000, public)"
	@echo "  make build      - Build frontend for production"
	@echo "  make deploy     - Deploy to Cloudflare Workers"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Lint code"

install:
	@echo "Installing dependencies..."
	pnpm install

start:
	@echo "Starting development servers..."
	pnpm dev:frontend

frontend:
	@echo "Starting frontend server on 0.0.0.0:3000..."
	cd apps/frontend && npx next dev -p 3000 -H 0.0.0.0

build:
	@echo "Building frontend for production..."
	pnpm build:frontend

deploy:
	@echo "Deploying to Cloudflare Workers..."
	cd apps/frontend && pnpm build && npx wrangler deploy

clean:
	@echo "Cleaning build artifacts..."
	rm -rf apps/frontend/.next
	rm -rf apps/frontend/.vercel
	rm -rf apps/frontend/.output
	rm -rf apps/backend/dist
	@echo "Done"

test:
	@echo "Running tests..."
	cd apps/frontend && pnpm test

lint:
	@echo "Linting code..."
	cd apps/frontend && pnpm lint
