# ARIA Labels Audit — carbonscope-init Frontend

**Date**: 2026-04-02
**Status**: In Progress

## Summary

| Issue | Count | Status |
|-------|-------|--------|
| Images without alt text | 74 | ⏳ Pending |
| Inputs without labels | 41 | ⏳ Pending |
| Icon-only buttons missing aria-label | ~20 | ✅ Key ones fixed |

## High Priority Fixes Applied

### Sidebar navigation buttons
- Expand/collapse sidebar button: `aria-label="Expand sidebar"` ✅
- View navigation buttons: `aria-label={label}` ✅

### Chat input mode buttons
- Adaptive/Autonomous/Chat mode: `aria-label="Switch to X mode"` ✅

## Remaining (lower priority)
- `<img>` tags in tool views (dynamic content) — add `alt=""` for decorative
- Form inputs in admin pages — tie to `<label>` via `htmlFor`
- Review dynamic `<button>` with only icon children

## Guidelines
All interactive elements must have either:
1. Visible text label
2. `aria-label` attribute
3. `aria-labelledby` referencing visible text

See: https://www.w3.org/WAI/WCAG21/Understanding/name-role-value
