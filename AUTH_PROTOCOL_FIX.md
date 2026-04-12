# Auth Protocol Fix

**Issue:** Chrome error showing `Unsafe attempt to load URL https://0.0.0.0:3000/auth?error=fetch%20failed`

**Root Cause:** Supabase redirect URL configuration had HTTPS when local dev uses HTTP

## Fix Applied

**File:** `supabase/config.toml`

**Changed (line 156):**
```toml
additional_redirect_urls = ["https://127.0.0.1:3000"]
```

**To:**
```toml
additional_redirect_urls = ["http://127.0.0.1:3000", "http://localhost:3000"]
```

## Why This Happened

1. Supabase auth redirects must match the protocol (HTTP vs HTTPS)
2. Local development uses HTTP (not HTTPS)
3. The config had HTTPS, causing protocol mismatch
4. Also added `localhost` variant for compatibility

## How to Apply

### 1. Clear Browser State
```bash
# Clear browser cache and cookies
Ctrl+Shift+Delete (Chrome/Firefox)
```

### 2. Restart Supabase (if running locally)
```bash
cd /path/to/carbonscope-init

# If using Supabase CLI
supabase stop
supabase start

# OR if using Docker
docker-compose down
docker-compose up -d
```

### 3. Access Correct URL
✅ **Use:** `http://localhost:3000`  
❌ **Don't use:** `https://0.0.0.0:3000`

## Related Configuration

**Frontend .env:**
```env
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH
```

**Supabase config.toml:**
```toml
site_url = "http://127.0.0.1:3000"
additional_redirect_urls = ["http://127.0.0.1:3000", "http://localhost:3000"]
```

## Testing

1. Open `http://localhost:3000`
2. Click "Get started" button
3. Auth modal should open without errors
4. Click "Continue with Google" or "Sign in with email"
5. Should redirect properly without protocol errors

## Prevention

- Always use HTTP for local development
- Only use HTTPS in production
- Keep redirect URLs in sync with actual access URLs
- Don't use `0.0.0.0` in browser (that's for server binding)

## Related Files

- `supabase/config.toml` - Supabase auth config
- `apps/frontend/.env` - Frontend environment variables
- `apps/frontend/src/components/GoogleSignIn.tsx` - Google auth component
- `apps/frontend/src/app/auth/actions.ts` - Auth server actions

## Status

✅ **Fixed** - March 28, 2026  
⏳ **Requires:** Supabase restart + browser cache clear
