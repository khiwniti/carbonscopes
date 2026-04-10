# Codebase Concerns

**Analysis Date:** 2026-04-09

## Tech Debt

**[Report Generation]:**
- Issue: In-memory report storage using global dictionary `_report_storage` in `backend/api/v1/reports.py`
- Files: `/workspaces/carbonscopes/backend/api/v1/reports.py` (lines 62-74)
- Impact: Reports lost on server restart, no persistence, scalability issues with memory usage
- Fix approach: Replace with database storage using Supabase, implement proper cleanup mechanisms

**[Mock Data in Reports]:**
- Issue: Report generation uses hardcoded mock data instead of actual database queries
- Files: `/workspaces/carbonscopes/backend/api/v1/reports.py` (lines 91-171, 174-204)
- Impact: Reports contain fake data, not suitable for production use
- Fix approach: Replace `get_analysis_data()` and `get_audit_trail()` functions with actual database queries using Supabase client

**[Temporary Web Search Tool Comments]:**
- Issue: TODO comment indicating incomplete functionality for subpage filtering
- Files: `/workspaces/carbonscopes/backend/core/tools/web_search_tool.py` (line 17)
- Impact: Limited search capabilities, may miss relevant information from subpages
- Fix approach: Implement subpage filtering as indicated in the TODO comment

## Known Bugs

**[Clipboard Functionality Missing]:**
- Symptoms: Webhook URL copy functionality shows toast message but doesn't actually copy to clipboard
- Files: `/workspaces/carbonscopes/apps/mobile/components/pages/TriggerDetailPage.tsx` (lines 220-223)
- Trigger: User attempts to copy webhook URL
- Workaround: Manual copy required
- Fix approach: Implement actual clipboard functionality using Expo Clipboard API

**[Profile Settings Not Implemented]:**
- Symptoms: Menu items for profile, briefcase, notifications, favorites, calendar show TODO comments
- Files: `/workspaces/carbonscopes/apps/mobile/hooks/ui/useSideMenu.ts` (lines 64-87)
- Trigger: User clicks on profile, briefcase, bell, star, or calendar icons
- Workaround: None available
- Fix approach: Implement navigation to corresponding settings/views

## Security Considerations

**[API Key Exposure Risk]:**
- Risk: Multiple API keys (TAVILY_API_KEY, FIRECRAWL_API_KEY, REPLICATE_API_TOKEN) accessed via config without validation
- Files: `/workspaces/carbonscopes/backend/core/tools/web_search_tool.py` (lines 109-117)
- Current mitigation: Warning logs when keys missing
- Recommendations: 
  - Validate API keys at startup and fail fast if missing
  - Implement key rotation mechanisms
  - Use environment-specific key management
  - Add rate limiting and usage monitoring

**[Insecure Temporary File Storage]:**
- Risk: Report files stored in system temp directory with predictable paths
- Files: `/workspaces/carbonscopes/backend/api/v1/reports.py` (lines 254-256, 399-409)
- Current mitigation: None beyond basic file existence checks
- Recommendations:
  - Use secure random directory names
  - Implement proper file permissions
  - Add automatic cleanup of expired files
  - Consider encrypting sensitive report data at rest

## Performance Bottlenecks

**[Web Search Image Processing]:**
- Problem: Image enrichment downloads and processes all images in parallel without limits
- Files: `/workspaces/carbonscopes/backend/core/tools/web_search_tool.py` (lines 390-393, 412-461)
- Cause: No concurrency limits on image processing, potential for resource exhaustion
- Improvement path: 
  - Add semaphore-based concurrency limiting
  - Implement image size filtering before processing
  - Add caching for frequently accessed images
  - Consider skipping image enrichment for certain use cases

**[Report Generation Temp Directory]:**
- Problem: Creates new directory for each report without cleanup mechanism
- Files: `/workspaces/carbonscopes/backend/api/v1/reports.py` (lines 254-256)
- Cause: Temporary directories accumulate over time
- Improvement path:
  - Implement background cleanup job
  - Set TTL for temporary files
  - Use managed temporary storage with automatic expiration

**[Progress Simulation in CompleteToolView]:**
- Problem: Fake progress animation that increments by 5% every 300ms regardless of actual progress
- Files: `/workspaces/carbonscopes/apps/frontend/src/components/thread/tool-views/CompleteToolView.tsx` (lines 50-65)
- Cause: Misleading UX, doesn't reflect actual tool execution progress
- Improvement path:
  - Connect progress bar to actual tool execution stages
  - Remove fake progress simulation
  - Show indeterminate progress for unknown duration tasks

## Fragile Areas

**[Agent Metrics Endpoint]:**
- Files: `/workspaces/carbonscopes/backend/api/v1/agents/metrics.py`
- Why fragile: 
  - Multiple TODO items indicating incomplete implementation
  - Hardcoded metric values that don't reflect actual system state
  - Database connection check always returns False
  - Prometheus status hardcoded to False
- Safe modification: 
  - Implement actual database session factory
  - Replace hardcoded values with real metrics collection
  - Add proper health check implementations
  - Connect to actual Prometheus endpoints when available
- Test coverage: Limited - appears to be mostly mock data

**[Trace Endpoint]:**
- Files: `/workspaces/carbonscopes/backend/api/v1/agents/traces.py`
- Why fragile:
  - TODO comment for database session factory implementation
  - Likely returns empty/mock data in production
- Safe modification:
  - Implement actual database session factory
  - Connect to real trace storage
  - Add proper error handling for database failures
- Test coverage: Unknown but likely minimal

## Scaling Limits

**[In-Memory Report Storage]:**
- Current capacity: Limited by server memory
- Limit: Application restart loses all reports, memory grows unbounded with usage
- Scaling path: 
  - Migrate to persistent storage (Supabase)
  - Implement report retention policies
  - Add pagination for report listing
  - Consider archiving old reports to cold storage

**[Web Search Concurrent Requests]:**
- Current capacity: Unlimited concurrent web searches and image processing
- Limit: Potential for resource exhaustion (memory, CPU, network) under heavy load
- Scaling path:
  - Implement request queuing and rate limiting
  - Add concurrency limits for web search operations
  - Implement circuit breaker pattern for external API calls
  - Add request timeout and cancellation mechanisms

## Dependencies at Risk

**[Tavily API]:**
- Risk: Web search functionality entirely dependent on Tavily API with no fallback
- Impact: Complete loss of web search capability if service unavailable or rate limited
- Migration plan:
  - Implement abstract search interface
  - Add support for alternative search providers (Google, Bing, DuckDuckGo)
  - Implement caching layer to reduce API calls
  - Add graceful degradation when search unavailable

**[Firecrawl API]:**
- Risk: Web scraping functionality entirely dependent on Firecrawl API
- Impact: Loss of webpage scraping capability
- Migration plan:
  - Implement abstract scraping interface
  - Add fallback to built-in HTTP client with HTML parsing
  - Consider open-source alternatives like playwright for complex sites
  - Implement rate limiting and retry logic

**[Replicate API (Moondream2)]:**
- Risk: Image understanding functionality dependent on Replicate API
- Impact: Loss of image OCR and description capabilities
- Migration plan:
  - Implement local OCR alternatives (Tesseract) as fallback
  - Add option to disable image enrichment
  - Implement local vision models for air-gapped environments
  - Add caching for image descriptions

## Missing Critical Features

**[Report Persistence]:**
- Problem: No permanent storage for generated reports
- Blocks: Production use, audit compliance, historical analysis
- What's missing: Database storage for report metadata and files

**[User Preferences and Settings]:**
- Problem: Mobile app has incomplete settings implementation (TODOs in useSideMenu)
- Blocks: Personalization, user configuration, accessibility features
- What's missing: Settings pages for profile, notifications, preferences

**[Actual Progress Reporting]:**
- Problem: Fake progress animations in tool views
- Blocks: Accurate user feedback, trust in system responsiveness
- What's missing: Real progress tracking tied to actual tool execution stages

## Test Coverage Gaps

**[Report Generation Logic]:**
- What's not tested: Actual database integration, error handling for storage failures
- Files: `/workspaces/carbonscopes/backend/api/v1/reports.py`
- Risk: Production failures undetected until deployment
- Priority: High

**[Web Search Error Handling]:**
- What's not tested: Network failures, API rate limiting, invalid responses
- Files: `/workspaces/carbonscopes/backend/core/tools/web_search_tool.py`
- Risk: Tool failures causing agent execution to break
- Priority: High

**[Mobile App Navigation]:**
- What's not tested: Profile, briefcase, notifications, favorites, calendar navigation
- Files: `/workspaces/carbonscopes/apps/mobile/hooks/ui/useSideMenu.ts`
- Risk: Broken user experience in production
- Priority: Medium

**[Agent Metrics Accuracy]:**
- What's not tested: Actual metric collection and reporting
- Files: `/workspaces/carbonscopes/backend/api/v1/agents/metrics.py`
- Risk: Misleading system health information
- Priority: Medium