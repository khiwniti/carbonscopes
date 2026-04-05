.PHONY: install install-backend install-frontend start stop status dev dev-frontend dev-backend docker-up docker-down docker-logs lint lint-backend lint-frontend test test-backend clean help

SHELL := /bin/bash
BACKEND_DIR := backend
FRONTEND_DIR := apps/frontend

help:
	@echo "CarbonScope Suna - Available commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install           Install all dependencies (backend + frontend)"
	@echo "  install-backend   Install backend Python dependencies with uv"
	@echo "  install-frontend  Install frontend Node dependencies with pnpm"
	@echo ""
	@echo "Development:"
	@echo "  start             Start all services (interactive)"
	@echo "  stop              Stop all services"
	@echo "  status            Show service status"
	@echo "  dev               Start development servers (backend + frontend)"
	@echo "  dev-frontend      Start frontend dev server only"
	@echo "  dev-backend       Start backend dev server only"
	@echo ""
	@echo "Docker:"
	@echo "  docker-up         Start all services with Docker Compose"
	@echo "  docker-down       Stop Docker Compose services"
	@echo "  docker-logs       View Docker logs (follow mode)"
	@echo ""
	@echo "Quality:"
	@echo "  lint              Run all linters"
	@echo "  lint-backend      Run backend linter (ruff)"
	@echo "  lint-frontend     Run frontend linter"
	@echo "  test              Run all tests"
	@echo "  test-backend      Run backend tests"
	@echo ""
	@echo "Other:"
	@echo "  clean             Clean generated files and caches"

install: install-backend install-frontend
	@echo "All dependencies installed."

install-backend:
	@echo "Installing backend dependencies..."
	cd $(BACKEND_DIR) && uv sync

install-frontend:
	@echo "Installing frontend dependencies..."
	bash scripts/fast-install.sh

start:
	@echo "Starting services..."
	python start.py start

stop:
	@echo "Stopping services..."
	python start.py stop

status:
	python start.py status

dev: dev-backend dev-frontend

dev-frontend:
	@echo "Starting frontend dev server..."
	pnpm dev:frontend

dev-backend:
	@echo "Starting backend dev server..."
	cd $(BACKEND_DIR) && uv run uvicorn api:app --reload --host 0.0.0.0 --port 8000

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

lint: lint-backend lint-frontend

lint-backend:
	cd $(BACKEND_DIR) && uv run ruff check core/

lint-frontend:
	cd $(FRONTEND_DIR) && pnpm lint

test: test-backend

test-backend:
	cd $(BACKEND_DIR) && uv run pytest

clean:
	@echo "Cleaning..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .setup_progress 2>/dev/null || true
	@echo "Clean complete."
