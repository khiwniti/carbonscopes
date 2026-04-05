.PHONY: verify check lint test-imports lint-fix

verify:
	@echo "Running build verification..."
	@uv run python core/utils/scripts/verify_build.py

check: verify

lint:
	@echo "Running ruff linter..."
	@uv run ruff check core/

lint-fix:
	@echo "Running ruff linter with auto-fix..."
	@uv run ruff check --fix core/

test-imports:
	@echo "Testing critical imports..."
	@uv run python core/utils/scripts/check_imports.py


test-utils:
	@echo "Running utils unit tests (fast, no external deps)..."
	@cd tests/utils && ../../.venv/bin/python -m pytest . -q --timeout=10

test-syntax:
	@echo "Checking Python syntax..."
	@.venv/bin/python -m py_compile $$(find core boq -name "*.py" | grep -v __pycache__) && echo "✅ All files OK"

fast-check: lint test-syntax test-utils
	@echo "✅ All fast checks passed"
