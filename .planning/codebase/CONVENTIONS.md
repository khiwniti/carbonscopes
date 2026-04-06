# Coding Conventions

**Analysis Date:** 2026-04-06

## Naming Patterns

**Files:**
- **React Components**: PascalCase for `.tsx` files - `AgentSelector.tsx`, `UserEmailLink.tsx`, `StatCard.tsx`
- **Utility modules**: kebab-case for `.ts` files - `use-agents.ts`, `agent-crud.ts`, `use-file-content.ts`
- **Python modules**: snake_case - `unit_normalizer.py`, `carbon_pipeline.py`, `audit_logger.py`
- **Test files**: `test_*.py` (Python), `*.test.ts` (TypeScript unit), `*.spec.ts` (Playwright E2E)
- **API routes**: kebab-case - `admin-api.py`, `agent-tools.ts`, `feedback-admin-api.py`
- **Configuration**: Dotfiles or `.config.*` - `.prettierrc`, `eslint.config.mjs`, `playwright.config.ts`

**Functions:**
- **TypeScript/JavaScript**: camelCase - `getAgents()`, `handleLoadMore()`, `propagateMergedCells()`, `detectHeaderRow()`
- **Python**: snake_case - `detect_header_row()`, `parse_boq()`, `get_redis_client()`, `warm_up_tools_cache()`
- **React Hooks**: `use` prefix + camelCase - `useAgents()`, `useMessages()`, `useFileContent()`, `useAgentStream()`
- **Event Handlers**: `handle` prefix + camelCase - `handleAgentSelect()`, `handleLoadMore()`, `onAgentSelect()`

**Variables:**
- **TypeScript/JavaScript**: camelCase - `selectedAgentId`, `isLoading`, `debouncedSearchQuery`, `currentPage`
- **Python**: snake_case - `file_path`, `mock_config`, `test_client`, `merged_map`
- **Constants**: UPPER_SNAKE_CASE - `MAX_CONCURRENT_IPS`, `DEFAULT_AGENT_PARAMS`, `NAV_OPTS`, `INSTANCE_ID`
- **Environment Variables**: UPPER_SNAKE_CASE - `ENV_MODE`, `SUPABASE_URL`, `REDIS_HOST`, `NODE_ENV`

**Types/Interfaces:**
- **TypeScript**: PascalCase - `AgentSelectorProps`, `AgentsParams`, `BOQParseResult`, `DashboardLayoutProps`
- **Python Classes**: PascalCase - `Agent`, `AgentRegistry`, `BOQMaterial`, `MockAgent`, `AgentState`

## Code Style

**Formatting:**
- **Tool**: Prettier for TypeScript/JavaScript
- **Config**: `apps/frontend/.prettierrc`
- **Settings**:
  - Semi-colons: `true`
  - Single quotes: `true`
  - Trailing commas: `all`
  - Tab width: `2`
  - Print width: `80`
- **Command**: `pnpm format` (write), `pnpm format:check` (verify)
- **Python**: Follows PEP 8 conventions (no explicit formatter configured)

**Linting:**
- **Tool**: ESLint with Next.js presets (`apps/frontend/eslint.config.mjs`)
- **Extends**: `next/core-web-vitals`, `next/typescript`
- **Key Rules**:
  - `@typescript-eslint/no-unused-vars`: `off` (warnings disabled)
  - `@typescript-eslint/no-explicit-any`: `off` (any type allowed)
  - `@typescript-eslint/no-empty-object-type`: `off`
  - `react/no-unescaped-entities`: `off`
  - `react-hooks/exhaustive-deps`: `warn` (hook dependency warnings)
  - `@next/next/no-img-element`: `warn` (prefer next/image)
  - `@next/next/no-html-link-for-pages`: `off`
  - `prefer-const`: `warn`
- **Command**: `pnpm lint`
- **Python**: No explicit linter configured (pytest markers suggest ruff or flake8 may be used)

**TypeScript Configuration:**
- **Config**: `apps/frontend/tsconfig.json`
- **Strict Mode**: `false` (lenient type checking)
- **Strict Null Checks**: `false` (null/undefined checks disabled)
- **Target**: ES2017
- **Module**: esnext
- **Module Resolution**: bundler
- **Skip Lib Check**: `true`
- **Allow JS**: `true`
- **JSX**: preserve
- **Isolated Modules**: `true`
- **Notes**: Relaxed TypeScript configuration prioritizing development speed over type safety

## Import Organization

**Order:**
1. **External dependencies** (React, third-party libraries)
2. **Internal UI components** (`@/components`)
3. **Hooks** (`@/hooks`)
4. **Utilities and helpers** (`@/lib`)
5. **Types and interfaces**
6. **Relative imports** (`./` or `../`)

**Path Aliases:**
- `@/*` → `apps/frontend/src/*`
- `@agentpress/shared` → `packages/shared/src/index.ts`
- `@agentpress/shared/*` → `packages/shared/src/*`

**Python Imports:**
- **Standard library first**: `os`, `sys`, `asyncio`, `datetime`
- **Third-party packages second**: `pytest`, `fastapi`, `openpyxl`
- **Local modules last**: `from .models import`, `from core.utils import`
- **Relative imports**: For same-package modules

**Examples:**
```typescript
// TypeScript component imports (apps/frontend/src/components/agents/agent-selector.tsx)
import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { Search, Plus, Check, ChevronDown } from 'lucide-react';
import { CarbonScopeLoader } from '@/components/ui/carbonscope-loader';
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent } from '@/components/ui/dropdown-menu';
import { useAgents } from '@/hooks/agents/use-agents';
import { NewAgentDialog } from '@/components/agents/new-agent-dialog';
import { cn } from '@/lib/utils';
```

```python
# Python imports (backend/boq/parser.py)
import openpyxl
import hashlib
import logging
from pathlib import Path
from decimal import Decimal, InvalidOperation
from typing import Optional
from datetime import datetime

from .models import BOQMaterial, BOQParseResult
from .unit_normalizer import normalize_unit
```

## Error Handling

**Patterns:**
- **TypeScript**: Try-catch with logger fallback
  ```typescript
  try {
    return Color.formatRGBA(Color.parse(cssColor));
  } catch (e) {
    logger.error('Color parsing failed:', e);
    return fallback;
  }
  ```
- **Python**: Docstring-documented exceptions
  ```python
  def parse_boq(file_path: str, encoding: str = 'utf-8') -> BOQParseResult:
      """
      Raises:
          FileNotFoundError: If file doesn't exist
          ValueError: If file format is invalid
      """
  ```
- **React Query**: Error boundaries and error states in hooks
- **FastAPI**: HTTPException with status codes and detail messages
  ```python
  from fastapi import HTTPException
  raise HTTPException(status_code=404, detail="Resource not found")
  ```

## Logging

**Framework:**
- **Frontend**: Custom logger (`@/lib/logger`)
- **Backend**: `structlog` v25.4.0 for structured logging

**Frontend Logging Patterns:**
- **Development**: All levels active (`log`, `info`, `warn`, `debug`, `error`)
- **Production**: Only `error` emits (others silenced via `NODE_ENV` check)
- **Usage**:
  ```typescript
  import { logger } from '@/lib/logger';
  logger.error('API call failed:', error);
  logger.info('User logged in', { userId });
  ```

**Backend Logging Patterns:**
- **Contextual logging** with structured data
- **Log levels**: `debug`, `info`, `warning`, `error`
  ```python
  logger.debug(f"Header row detected at line {row_idx + 1} (Thai)")
  logger.info(f"[STARTUP] Cleared {len(all_keys)} tier caches")
  logger.warning(f"Failed to warm up database connection pool: {e}")
  logger.error(f"Failed to initialize Redis connection: {e}")
  ```

**When to Log:**
- **Critical errors**: Always (both frontend and backend)
- **State transitions**: Info level (startup, shutdown, major operations)
- **Debug information**: Debug level (development only)
- **User-facing errors**: Error level with user-friendly messages

## Comments

**When to Comment:**
- **File-level docstrings**: Purpose and responsibility
  ```python
  """
  Thai BOQ Excel Parser.
  
  Handles complex Thai construction BOQ files with merged cells,
  bilingual headers, and mixed unit formats.
  """
  ```
- **Function docstrings**: Purpose, parameters, return values, exceptions
  ```python
  def detect_header_row(sheet) -> Optional[int]:
      """
      Detect BOQ header row by searching for Thai/English keywords.

      Searches for: รายการ, หน่วย, จำนวน (Thai) or
                    description, unit, quantity (English)

      Returns row index (0-based) or None if not found.
      """
  ```
- **Complex logic**: Non-obvious algorithms or business rules
- **Type annotations**: TypeScript interfaces for component props
  ```typescript
  interface AgentSelectorProps {
    selectedAgentId?: string;
    onAgentSelect: (agentId: string) => void;
    placeholder?: string;
    className?: string;
    disabled?: boolean;
    showCreateOption?: boolean;
    variant?: 'default' | 'compact';
  }
  ```
- **Test descriptions**: Clear test intent
  ```typescript
  /**
   * Unit tests for logger.ts (#116)
   * Tests that production mode silences log/warn/info/debug but always passes error.
   */
  ```

**JSDoc/TSDoc:**
- **Minimal usage**: TypeScript types provide most documentation
- **Used for**: Complex utility functions, public APIs, important clarifications
- **Not strictly enforced**: No mandatory documentation requirements

## Function Design

**Size:**
- **Preference**: Functions under 50 lines for utilities
- **Observed**: Mix of small focused functions and larger component functions
- **React Components**: 100-300 lines acceptable (includes JSX, state, effects)
- **Backend Functions**: Typically 20-100 lines

**Parameters:**
- **TypeScript**: Object parameters for multiple optional params
  ```typescript
  export const useAgents = (
    params: AgentsParams = {},
    customOptions?: UseQueryOptions
  ) => { ... }
  ```
- **Python**: Explicit parameters with type hints and defaults
  ```python
  def parse_boq(
      file_path: str,
      encoding: str = 'utf-8'
  ) -> BOQParseResult:
  ```

**Return Values:**
- **TypeScript**: Explicit return types for hooks and utilities
- **Python**: Type-hinted return values (`-> ReturnType`)
- **React Hooks**: Return objects or arrays with clear destructuring patterns
  ```typescript
  const { data, isLoading, error } = useAgents(params);
  ```

## Module Design

**Exports:**
- **Named exports preferred** over default exports (TypeScript/JavaScript)
  ```typescript
  export const AgentSelector: React.FC<AgentSelectorProps> = ({ ... }) => { ... }
  export { truncateString } from '@/lib/shared/utils';
  ```
- **Default exports**: Used for Next.js pages and layout components
  ```typescript
  export default function DashboardLayout({ children }: DashboardLayoutProps) { ... }
  ```
- **Python**: Always named exports
  ```python
  from .models import BOQMaterial, BOQParseResult
  from .parser import parse_boq
  ```

**Barrel Files:**
- **Usage**: `index.ts` files for hook directories and components
  ```
  apps/frontend/src/hooks/agents/index.ts
  apps/frontend/src/hooks/admin/index.ts
  apps/frontend/src/components/agents/index.ts
  ```
- **Purpose**: Centralized exports, cleaner imports
- **Python**: `__init__.py` files for package initialization

## React Patterns

**Component Style:**
- **Functional components** with TypeScript
- **`React.FC` type** for components with props
- **Hooks-based** state management (no class components observed)
- **`'use client'` directive** for client-side interactive components

**State Management:**
- **Local state**: `useState`, `useRef` for component-local data
- **Server state**: React Query (`@tanstack/react-query`) for API data
- **Global state**: Zustand v5.0.3 for client-side global state
- **Memoization**: `useMemo`, `useCallback` for optimization

**Optimization:**
- `useMemo` for expensive computations (filtering, sorting)
  ```typescript
  const normalizedParams = useMemo(() => {
    // Normalize params logic
  }, [params]);
  ```
- `useCallback` for stable function references
  ```typescript
  const handleLoadMore = useCallback(() => {
    if (canLoadMore && !isFetching) {
      setCurrentPage(prev => prev + 1);
    }
  }, [canLoadMore, isFetching]);
  ```
- **Debouncing** for search inputs (300ms standard delay)
  ```typescript
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
      setCurrentPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);
  ```

**Client Directives:**
- `'use client'` for interactive components using hooks
- `server-only` import for server-side utilities

## Python Patterns

**Type Hints:**
- **Comprehensive usage** for function signatures
- **Generic types**: `dict[str, any]`, `set[str]`, `list[str]`, `Optional[int]`
- **Return type annotations**: Always specified
  ```python
  def detect_header_row(sheet) -> Optional[int]:
  async def execute(self, state: AgentState) -> dict[str, any]:
  ```

**Async Patterns:**
- **AsyncIO**: `async def` for async functions
- **Pytest-asyncio**: `@pytest.mark.asyncio` for async tests
- **FastAPI**: Async route handlers
  ```python
  @router.get("/health")
  async def health_check():
      return {"status": "healthy"}
  ```

**Testing Patterns:**
- **Fixtures**: Pytest fixtures for shared test setup
  ```python
  @pytest.fixture
  def mock_state():
      return {"user_query": "Test query", ...}
  ```
- **Mocking**: `unittest.mock.Mock`, `MagicMock` for dependencies
- **Markers**: Custom markers for test categorization
  ```python
  @pytest.mark.asyncio
  @pytest.mark.integration
  async def test_full_flow():
  ```

**Docstring Format:**
- **Google-style** docstrings for functions
  ```python
  """
  Parse Thai BOQ Excel file.

  Args:
      file_path: Absolute path to .xlsx or .xls file
      encoding: Character encoding (default utf-8)

  Returns:
      BOQParseResult with parsed materials and metadata

  Raises:
      FileNotFoundError: If file doesn't exist
      ValueError: If file format is invalid
  """
  ```

---

*Convention analysis: 2026-04-06*
