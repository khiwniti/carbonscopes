.PHONY: install install-backend install-frontend start stop status dev dev-frontend dev-backend docker-up docker-down docker-logs lint lint-backend lint-frontend test test-backend clean help

SHELL := /bin/bash
BACKEND_DIR := backend
FRONTEND_DIR := apps/frontend

help:
	@echo "CarbonScope - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  dev               Start all services in parallel (honcho)"
	@echo "  dev-backend       Start backend only (port 8000)"
	@echo "  dev-frontend      Start frontend only (port 3000)"
	@echo ""
	@echo "Installation:"
	@echo "  install           Install all dependencies"
	@echo "  install-backend   Install backend Python deps (uv)"
	@echo "  install-frontend  Install frontend Node deps (pnpm)"
	@echo ""
	@echo "Docker:"
	@echo "  docker-up         Start all services with Docker Compose"
	@echo "  docker-down       Stop Docker Compose services"
	@echo "  docker-logs       View Docker logs (follow mode)"
	@echo ""
	@echo "Quality:"
	@echo "  lint              Run all linters"
	@echo "  test              Run all tests"
	@echo "  clean             Clean caches"

# ── Development ──────────────────────────────────────────────────────────────

dev:
	@lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null; true
	@lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null; true
	@sleep 0.5
	@echo "Starting all services in parallel..."
	honcho start

dev-backend:
	@echo "Starting backend..."
	cd $(BACKEND_DIR) && uv run uvicorn api:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend..."
	cd $(FRONTEND_DIR) && pnpm dev --port 3000

start:
	honcho start

stop:
	@lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
	@lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null || true
	@pkill -f "uvicorn api:app" 2>/dev/null || true
	@pkill -f "next dev" 2>/dev/null || true
	@sleep 0.5
	@echo "Services stopped."

status:
	@echo "Backend:  $$(curl -s http://localhost:8000/health | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get(\"status\",\"ok\"))' 2>/dev/null || echo 'not running')"
	@echo "Frontend: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 2>/dev/null || echo 'not running')"

# ── Installation ──────────────────────────────────────────────────────────────

install: install-backend install-frontend
	@echo "All dependencies installed."

install-backend:
	@echo "Installing backend dependencies..."
	cd $(BACKEND_DIR) && uv sync

install-frontend:
	@echo "Installing frontend dependencies..."
	bash scripts/fast-install.sh

# ── Docker ────────────────────────────────────────────────────────────────────

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

# ── Quality ───────────────────────────────────────────────────────────────────

lint: lint-backend lint-frontend

lint-backend:
	cd $(BACKEND_DIR) && uv run ruff check core/

lint-frontend:
	cd $(FRONTEND_DIR) && pnpm lint

test: test-backend

test-backend:
	cd $(BACKEND_DIR) && uv run pytest

# ── Cleanup ───────────────────────────────────────────────────────────────────

clean:
	@echo "Cleaning..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .setup_progress 2>/dev/null || true
	@echo "Clean complete."
