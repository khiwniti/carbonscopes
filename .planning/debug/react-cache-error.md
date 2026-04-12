---
status: diagnosed
trigger: "Investigate issue: React.cache is not a function error. Frontend compilation succeeds but runtime error occurs: \"TypeError: (0 , _react.cache) is not a function\" on the home page."
created: 2026-04-10T14:55:04+00:00
updated: 2026-04-10T14:58:00+00:00
---

## Current Focus
hypothesis: next-intl v4.5.3 requires React 19, but project is on React 18
test: Verified next-intl 4.5.3 uses React.cache internally which only exists in React 19+
expecting: Root cause confirmed
next_action: Return diagnosis

## Symptoms
expected: Frontend should load without runtime errors
actual: Compiles successfully but throws runtime error on page load
errors: TypeError: (0 , _react.cache) is not a function at __webpack_exec__ (.next/server/app/(home)/page.js:4609:39)
reproduction: Load the home page '/'
started: After fixing the multiple next.config files issue and cleaning build cache

## Eliminated
- hypothesis: App code is calling React.cache directly
  evidence: Grepped entire frontend codebase, no direct usage found. Checked home page components: page.tsx, background-aal-checker.tsx, hero-section.tsx - none use React.cache
  timestamp: 2026-04-10T14:57:00+00:00

## Evidence
- timestamp: 2026-04-10T14:56:00+00:00
  checked: package.json versions
  found: React 18.3.x installed, next-intl 4.5.3 installed
  implication: next-intl v4.x requires React 19, which introduces the React.cache() API
- timestamp: 2026-04-10T14:57:30+00:00
  checked: next-intl release notes
  found: next-intl 4.0.0+ uses React.cache internally for translations memoization, which only exists in React 19
  implication: This version is incompatible with React 18

## Resolution
root_cause: next-intl v4.5.3 was installed which requires React 19+, but the project is using React 18.x. next-intl internally uses `React.cache()` which does not exist in React 18, causing the runtime TypeError even though compilation succeeds.
fix: Downgrade next-intl to v3.x which supports React 18, or upgrade React and Next.js to React 19 compatible versions.
verification: Confirmed next-intl 4.x requires React 19, no usage of React.cache in application code
files_changed: []


## Symptoms
expected: Frontend should load without runtime errors
actual: Compiles successfully but throws runtime error on page load
errors: TypeError: (0 , _react.cache) is not a function at __webpack_exec__ (.next/server/app/(home)/page.js:4609:39)
reproduction: Load the home page '/'
started: After fixing the multiple next.config files issue and cleaning build cache

## Eliminated

## Evidence

## Resolution
root_cause:
fix:
verification:
files_changed: []
