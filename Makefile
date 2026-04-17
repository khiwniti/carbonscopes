# CarbonScopes Makefile
.PHONY: help install dev frontend build deploy clean test lint

help:
	@echo "CarbonScopes - Available Commands:"
	@echo "  make install    - Install all dependencies"
	@echo "  make dev        - Start development servers"
	@echo "  make frontend   - Start frontend only (port 3000)"
	@echo "  make build      - Build for production"
	@echo "  make deploy     - Deploy to Cloudflare Workers"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make test       - Run tests"

install:
	@echo "Installing dependencies..."
	pnpm install

dev:
	@echo "Starting development servers..."
	pnpm dev

frontend:
	@echo "Starting frontend server..."
	cd apps/frontend && pnpm dev

build:
	@echo "Building for production..."
	pnpm build

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
	pnpm test

lint:
	@echo "Linting code..."
	pnpm lint
