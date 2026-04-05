# Frontend Timeout Configuration

## Overview

All timeout values have been centralized in `/src/config/timeouts.ts` for better maintainability and environment-specific tuning.

## Configuration File

**Location**: `src/config/timeouts.ts`

### Timeout Categories

#### 1. UI Feedback & Animations
- `MOBILE_BANNER_SHOW`: 500ms - Delay before showing mobile app banner
- `MOBILE_BANNER_HIDE`: 300ms - Delay before hiding mobile app banner after close
- `TOAST_DURATION`: 3000ms - Duration for showing toast notifications
- `LOADING_DEBOUNCE`: 500ms - Debounce delay for loading indicators
- `FOCUS_DELAY`: 50ms - Focus delay for search inputs and modals
- `STEP_TRANSITION`: 500ms - Delay for step transitions in multi-step processes
- `CELEBRATION_DURATION`: 4000ms - Duration for celebration animations
- `AUTOPLAY_DELAY`: 2000ms - Delay for triggering autoplay in carousels
- `TYPING_INTERVAL`: 100ms - Interval for typing animation effects
- `SLIDE_TRANSITION`: 3000ms - Duration for example showcase slide transitions

#### 2. Auth & Navigation
- `GITHUB_POPUP_CHECK`: 1000ms - Interval for checking GitHub OAuth popup status
- `AUTH_REDIRECT_DELAY`: 2000ms - Delay before redirecting after authentication
- `DIALOG_AUTO_CLOSE`: 2000ms - Delay before closing dialogs after successful operation
- `POPUP_STATUS_CHECK`: 500ms - Interval for checking popup window status during OAuth

#### 3. Polling & Background Tasks
- `MAINTENANCE_CHECK`: 30000ms - Interval for checking maintenance countdown status
- `SEARCH_DEBOUNCE`: 300ms - Debounce delay for search input
- `OTP_COUNTDOWN_INTERVAL`: 1000ms - Interval for OTP resend countdown timer
- `CHECKOUT_POLL_INTERVAL`: 1000ms - Interval for checkout status polling
- `CHECKOUT_TIMEOUT`: 300000ms - Timeout for checkout completion (5 minutes)
- `ROUTE_CHANGE_DELAY`: 2000ms - Interval for route change tracking

#### 4. State Management
- `STATE_UPDATE_DELAY`: 0ms - Delay for triggering state updates in React components
- `SCHEDULE_UPDATE_DELAY`: 0ms - Delay for triggering schedule changes

## Usage

### Importing

```typescript
import { TIMEOUTS } from '@/config/timeouts';
```

### Basic Usage

```typescript
// Instead of:
setTimeout(() => setIsVisible(true), 500);

// Use:
setTimeout(() => setIsVisible(true), TIMEOUTS.MOBILE_BANNER_SHOW);
```

### With Helper Function

```typescript
import { TIMEOUTS, getTimeout } from '@/config/timeouts';

// Get timeout with multiplier
const doubleDelay = getTimeout('LOADING_DEBOUNCE', 2); // 1000ms
```

## Files Updated

### Updated Files (7 files)
1. `src/app/auth/github-popup/page.tsx` - GitHub OAuth popup timeouts
2. `src/app/checkout/page.tsx` - Checkout polling and timeout
3. `src/app/share/[threadId]/_components/MobileAppBanner.tsx` - Mobile banner delays
4. `src/components/announcements/maintenance-countdown-banner.tsx` - Maintenance polling
5. `src/components/agents/triggers/event-based-trigger-dialog.tsx` - Dialog auto-close
6. `src/components/agents/json-import-dialog.tsx` - Step transitions
7. `src/components/agents/installation/streamlined-install-dialog.tsx` - Step transitions

### Total Replacements
- **Frontend**: 13 timeout references using config
- **Files with imports**: 7 files

## Environment Configuration

Currently, timeouts are hardcoded in the config file. To make them environment-configurable:

1. Add environment variables to `.env`:
```env
NEXT_PUBLIC_AUTH_REDIRECT_DELAY=2000
NEXT_PUBLIC_CHECKOUT_TIMEOUT=300000
```

2. Update `timeouts.ts`:
```typescript
export const TIMEOUTS = {
  AUTH_REDIRECT_DELAY: parseInt(process.env.NEXT_PUBLIC_AUTH_REDIRECT_DELAY || '2000'),
  // ...
} as const;
```

## Testing

All timeout values are functionally tested through the existing E2E test suite:
- Authentication flows validate popup and redirect delays
- Checkout process tests validate polling intervals
- UI component tests validate animation and transition timing

## Maintenance

### Adding New Timeouts

1. Add constant to `src/config/timeouts.ts`:
```typescript
export const TIMEOUTS = {
  // ... existing timeouts
  NEW_FEATURE_DELAY: 1000,
} as const;
```

2. Import and use in your component:
```typescript
import { TIMEOUTS } from '@/config/timeouts';

setTimeout(() => doSomething(), TIMEOUTS.NEW_FEATURE_DELAY);
```

### Adjusting Values

Edit values in `src/config/timeouts.ts`. Consider:
- **User Experience**: Longer delays for critical operations, shorter for feedback
- **Network Conditions**: Increase polling intervals for slower networks
- **Accessibility**: Ensure sufficient time for users to read messages
- **Performance**: Balance responsiveness with resource usage

## Migration Notes

### Before (Hardcoded)
```typescript
setTimeout(() => window.close(), 500);
setInterval(updateStatus, 30000);
```

### After (Configured)
```typescript
import { TIMEOUTS } from '@/config/timeouts';

setTimeout(() => window.close(), TIMEOUTS.POPUP_STATUS_CHECK);
setInterval(updateStatus, TIMEOUTS.MAINTENANCE_CHECK);
```

## Benefits

1. **Centralized Management**: All timeouts in one place
2. **Semantic Naming**: Clear purpose for each timeout
3. **Easy Tuning**: Adjust values without hunting through codebase
4. **Environment-Ready**: Can be made environment-configurable
5. **Type Safety**: TypeScript ensures correct timeout keys
6. **Documentation**: Each timeout includes purpose comment
