# Codebase Concerns

**Analysis Date:** 2026-04-06

## Tech Debt

**Incomplete Implementation - Phase-Based TODOs:**
- Issue: Multiple "Phase 5" TODOs indicate incomplete integration with actual databases and cost systems
- Files: 
  - `backend/agents/alternatives_engine.py:388` - Cost database integration pending
  - `backend/agents/alternatives_engine.py:424` - Knowledge graph integration missing
  - `backend/agents/alternatives_api.py:105` - GraphDB and TGO database clients not initialized
  - `backend/agents/scenarios_api.py:95` - Checkpointer and carbon calculator placeholders
  - `backend/core/agents/compliance_agent.py:122` - Knowledge graph SPARQL queries not integrated
  - `backend/core/agents/sustainability_agent.py:194` - Alternatives engine integration missing
  - `backend/core/agents/report_generator_agent.py:81` - Phase 5 implementation pending
  - `backend/core/agents/boq_parser_agent.py:76` - Phase 2 parser integration incomplete
  - `backend/core/agents/cost_analyst_agent.py:113` - Cost database integration pending
- Impact: Core business logic using placeholder data instead of real calculations, affects accuracy of carbon calculations and cost estimates
- Fix approach: Prioritize Phase 5 integration work, implement actual database clients, replace placeholder logic with real implementations

**Infrastructure Configuration Gap:**
- Issue: Docker Compose lacks local Supabase integration
- Files: `docker-compose.yaml:10` - TODO comment indicating network configuration complexity
- Impact: Forces developers to use cloud Supabase or run without Docker, inconsistent development environments
- Fix approach: Integrate Supabase services into compose file with proper network configuration, document network setup

**Excessive Console Logging:**
- Issue: 383 console.log/error/warn statements across 151 TypeScript files
- Files: Widespread across `apps/frontend/src/components/**`, `apps/mobile/**`, `packages/shared/**`
- Impact: Production performance degradation, potential sensitive data exposure, difficult debugging
- Fix approach: Implement proper logging library (already exists at `apps/frontend/src/lib/logger.ts`), replace console statements with logger calls, configure log levels per environment

**TypeScript Type Safety Violations:**
- Issue: 749 occurrences of @ts-ignore, @ts-nocheck, any types across 250 files
- Files: Widespread across `apps/frontend/**`, `apps/mobile/**`, `packages/shared/**`
- Impact: Defeats TypeScript's type safety, hidden runtime errors, difficult refactoring
- Fix approach: Systematic type definition improvements, remove any types with proper interfaces, address underlying type issues instead of suppressing

**Broad Exception Handling:**
- Issue: 1242 instances of bare except or except Exception in Python code
- Files: Throughout `backend/` directory - `core/**`, `api/**`, `agents/**`, `lca/**`
- Impact: Swallows specific errors, difficult debugging, potential silent failures
- Fix approach: Replace with specific exception types, add proper logging, implement error recovery strategies

**Missing Python Package:**
- Issue: @babel/types dependency missing at root level
- Files: `package.json:10` declares dependency but npm outdated shows MISSING
- Impact: Build failures, inconsistent development environment
- Fix approach: Run npm install to install missing dependencies

## Known Bugs

**Sandbox File Access Bug:**
- Issue: Documented bug where files won't be accessible in sandbox resolver
- Files: `backend/tests/sandbox_resolver_test.py:152` - "This is a BUG - files won't be accessible!"
- Trigger: Sandbox file resolution logic error
- Workaround: None documented
- Priority: High - affects core sandbox functionality

**User ID Authentication Gap:**
- Issue: User ID hardcoded or not retrieved from authentication
- Files: `backend/agents/scenarios_api.py:134` - TODO comment indicates missing auth integration
- Trigger: API calls requiring user context
- Impact: Security risk, multi-tenant data isolation failure
- Priority: Critical - security vulnerability

## Security Considerations

**Environment File Template Security:**
- Risk: Environment templates contain placeholder secrets that could be committed
- Files:
  - `infra/environments/prod/.env.example:16` - Contains AWS ARN placeholders
  - `apps/frontend/.env.local.template` - API key placeholders
  - `apps/desktop/.env.example` - Credential templates
- Current mitigation: .gitignore excludes .env files, but templates exist
- Recommendations: Add pre-commit hooks to scan for accidentally committed secrets, document secret management procedures

**Dynamic Code Execution:**
- Risk: Use of code execution functions and dynamic imports in multiple files
- Files: 
  - `backend/core/tools/sb_*_tool.py` - Multiple sandbox tools use dynamic imports
  - `backend/core/agents/pipeline/stateless/coordinator/execution.py` - Dynamic execution patterns
  - `backend/evals/__init__.py` - Dynamic module loading
- Current mitigation: Appears to be in sandbox/evaluation contexts
- Recommendations: Audit all dynamic execution for user input sanitization, implement whitelist-based execution, add security review for sandbox escape scenarios

**Deprecated Package Vulnerabilities:**
- Risk: Multiple packages with known security vulnerabilities
- Files: 
  - `pnpm-lock.yaml:8108,8117,8122` - Old glob versions with "widely publicized security vulnerabilities"
  - `pnpm-lock.yaml:11718,11723` - Old tar versions with security issues
  - `pnpm-lock.yaml:5869,5874` - Packages with "critical issues"
- Current mitigation: None - packages still in use
- Recommendations: Upgrade vulnerable packages immediately, run security audit (npm audit, pip-audit), establish dependency update schedule

**Broad Exception Handling Hiding Security Issues:**
- Risk: Generic exception handlers could mask security-relevant errors
- Files: Throughout backend codebase (1242 occurrences)
- Current mitigation: None
- Recommendations: Implement security-specific exception handling, add security event logging, review error handlers in authentication/authorization paths

## Performance Bottlenecks

**Excessive setTimeout Usage:**
- Problem: 525 setTimeout/time.sleep calls across codebase
- Files: Widespread in `apps/frontend/**`, `apps/mobile/**`, `backend/**`
- Cause: Polling patterns, artificial delays, timing workarounds
- Impact: UI sluggishness, resource waste, scalability issues
- Improvement path: Replace polling with event-driven patterns, use proper async/await, remove artificial delays

**Placeholder Cost Calculations:**
- Problem: Cost estimation using hardcoded percentages instead of real calculations
- Files: `backend/agents/alternatives_engine.py:388-391` - Returns fixed 8.5% cost estimate
- Cause: Phase 5 integration incomplete
- Impact: Inaccurate business calculations, unreliable cost projections
- Improvement path: Implement actual cost database integration, add caching layer for cost lookups

**No Response Caching Strategy:**
- Problem: Repeated API calls without caching mechanism evident
- Files: Multiple API endpoints without cache headers or strategies
- Cause: Missing cache layer implementation
- Impact: Increased latency, higher database load, poor scalability
- Improvement path: Implement Redis caching for frequently accessed data, add HTTP cache headers, implement query result caching

## Fragile Areas

**Alternatives Engine Placeholder Logic:**
- Files: 
  - `backend/agents/alternatives_engine.py` - Multiple hardcoded assumptions
  - `backend/agents/alternatives_api.py:107` - Uninitialized database clients
- Why fragile: Using mock data, no real database connections, hardcoded compatibility scores
- Safe modification: Add integration tests before changing, implement actual database layer first, maintain backward compatibility
- Test coverage: Incomplete - relies on placeholder data

**BIM/LCA Calculation Pipeline:**
- Files:
  - `backend/lca/carbon_calculator.py` - Core calculation logic
  - `backend/boq/carbon_pipeline.py` - Bill of quantities processing
  - `backend/certification/trees.py` - Certification tree structures
- Why fragile: Complex domain logic, integration with external databases (Brightway2, GraphDB), version-specific compatibility issues
- Safe modification: Extensive unit tests required, validate against known reference calculations, maintain calculation audit trail
- Test coverage: Some tests exist (`backend/lca/tests/**`) but gaps in integration testing

**Frontend Streaming and Real-time Features:**
- Files:
  - `packages/shared/src/streaming/**` - Core streaming logic
  - `apps/frontend/src/lib/streaming/**` - Frontend stream handlers
  - `apps/frontend/src/components/presence-provider.tsx` - Real-time presence
- Why fragile: Complex state management, WebSocket connections, error recovery logic
- Safe modification: Test reconnection scenarios, validate state consistency, handle edge cases (network failures, server restarts)
- Test coverage: Limited observable test coverage for streaming edge cases

## Scaling Limits

**Sandbox Pool Resource Management:**
- Current capacity: Pool-based sandbox allocation
- Limit: Fixed pool size, no dynamic scaling evident
- Files: `backend/core/sandbox/pool_service.py`, `backend/core/sandbox/pool_background.py`
- Scaling path: Implement auto-scaling pool management, add resource limits per user, implement sandbox recycling

**Redis Single-Instance Dependency:**
- Current capacity: Single Redis instance for caching, sessions, pub/sub
- Limit: Single point of failure, memory constraints, no sharding
- Files: `backend/core/services/redis.py`, `docker-compose.yaml:28` - Redis configuration
- Scaling path: Implement Redis Cluster or Sentinel, add connection pooling, separate concerns (cache vs. sessions vs. pub/sub)

**GraphDB Query Performance:**
- Current capacity: Direct SPARQL queries without optimization
- Limit: Complex graph traversals, no query result caching evident
- Files: `backend/core/knowledge_graph/graphdb_client.py`, `backend/core/knowledge_graph/edge_trees_performance_tests.py`
- Scaling path: Implement query result caching, optimize SPARQL queries, add query complexity limits, consider graph database indexing strategy

## Dependencies at Risk

**Deprecated Novu Packages:**
- Risk: End of support April 3, 2025 (already passed)
- Impact: Security vulnerabilities, no updates, migration required
- Files: 
  - `pnpm-lock.yaml:2812` - @novu/client deprecated
  - `pnpm-lock.yaml:2829` - @novu/notification-center deprecated
- Migration plan: Migrate to @novu/react or @novu/js following official migration guide at https://docs.novu.co/platform/inbox/react/migration-guide

**Ontopy Python 2 Incompatibility:**
- Risk: Package removed due to Python 2 only support
- Impact: Knowledge graph ontology features unavailable
- Files: `backend/pyproject.toml:113` - Commented out with note "Python 2 only, incompatible with Python 3.12"
- Migration plan: Replace with owlready2 (already included) or find Python 3 compatible alternative for ontology operations

**Brightway2 Version Constraint:**
- Risk: Pinned to less than 2.5.0 for Python 3.12 compatibility
- Impact: Missing newer features, potential security updates unavailable
- Files: `backend/pyproject.toml:119` - Version constraint comment
- Migration plan: Monitor Brightway2 updates for Python 3.12 support, test upgrade path when available, consider alternative LCA libraries if stagnant

**Multiple Deprecated Glob/Tar/Rimraf:**
- Risk: Security vulnerabilities in file system utilities
- Impact: Potential file traversal attacks, security exploits
- Files: Multiple entries in pnpm-lock.yaml and infra/package-lock.json
- Migration plan: Run npm audit fix, update to latest versions, test file operations after updates

## Missing Critical Features

**Metrics and Observability Integration:**
- Problem: Prometheus client included but not fully configured
- Files: `backend/api/v1/agents/metrics.py:297-298` - TODOs for database connection and Prometheus checks
- Blocks: Production monitoring, performance tracking, alerting capabilities
- Priority: High - needed for production operations

**Comprehensive Error Tracking:**
- Problem: No centralized error tracking system evident
- Files: Logger exists (`backend/core/utils/logger.py`) but no error aggregation service integration
- Blocks: Production debugging, error trend analysis, user-facing error reporting
- Priority: Medium - important for production support

**API Rate Limiting:**
- Problem: Limited rate limiting implementation
- Files: slowapi dependency exists but implementation coverage unclear
- Blocks: API abuse prevention, fair resource allocation, cost control
- Priority: High - critical for production API protection

**Automated Backup Strategy:**
- Problem: No automated backup configuration evident
- Files: Database and file storage configurations lack backup directives
- Blocks: Disaster recovery, data loss prevention, compliance requirements
- Priority: High - critical for data integrity

## Test Coverage Gaps

**LCA Calculation Testing:**
- What's not tested: End-to-end carbon calculation workflows with real database integration
- Files: 
  - `backend/lca/**` - Core LCA logic
  - `backend/lca/tests/test_deterministic.py` - Some tests exist but integration gaps
- Risk: Inaccurate carbon calculations go undetected, regulatory compliance failures
- Priority: High - core business logic

**Streaming Edge Cases:**
- What's not tested: WebSocket reconnection, message ordering, partial message handling
- Files: 
  - `packages/shared/src/streaming/**`
  - `apps/frontend/src/lib/streaming/**`
- Risk: User experience degradation, message loss, state inconsistency
- Priority: Medium - affects user experience but not data integrity

**Authentication Flow Coverage:**
- What's not tested: Multi-factor authentication, session management edge cases, concurrent login handling
- Files: 
  - `backend/core/auth/**`
  - `apps/frontend/src/app/auth/**`
- Risk: Security vulnerabilities, authentication bypass scenarios
- Priority: High - security critical

**Sandbox Isolation:**
- What's not tested: Sandbox escape scenarios, resource limit enforcement, malicious code execution
- Files: 
  - `backend/core/sandbox/**`
  - `backend/tests/sandbox_timing_test.py` - Performance tests exist but security testing gaps
- Risk: Security breaches, resource exhaustion, cross-tenant data access
- Priority: Critical - security and multi-tenancy critical

**API Contract Compatibility:**
- What's not tested: Backward compatibility with older API clients, versioning strategy
- Files: 
  - `apps/frontend/src/__tests__/compatibility/api-contract.test.ts` - Tests exist but limited coverage
  - `backend/api/**` - API endpoints
- Risk: Breaking changes for existing clients, integration failures
- Priority: Medium - important for API stability

---

*Concerns audit: 2026-04-06*
