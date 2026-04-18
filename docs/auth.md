# Authentication Architecture

## Overview

CarbonScopes uses **Supabase Auth** for both frontend and backend authentication. This provides a unified auth system with JWT tokens.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Frontend      │         │   Supabase Auth  │         │   Backend       │
│  (Next.js)      │────────▶│   (JWKS/ES256)   │◀────────│  (FastAPI)      │
│                 │         │                  │         │                 │
│ - Login with    │         │ - Issues JWT     │         │ - Validates JWT │
│   OAuth         │         │ - Stores user    │         │ - Uses JWKS     │
│ - Stores token  │         │ - Manages        │         │ - RBAC roles    │
│   in browser    │         │   sessions       │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

## Authentication Flow

### 1. Login (Frontend)
```typescript
// User clicks "Sign in with Google/GitHub"
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'google', // or 'github'
  options: {
    redirectTo: `${window.location.origin}/auth/callback`
  }
})
```

### 2. Callback (Frontend)
```typescript
// Auth callback route handles the OAuth callback
// Supabase automatically exchanges the code for a session
```

### 3. API Requests (Frontend)
```typescript
// API client automatically adds Authorization header
const { data: { session } } = await supabase.auth.getSession()
headers['Authorization'] = `Bearer ${session.access_token}`
```

### 4. Validation (Backend)
```python
# Backend validates JWT using Supabase JWKS
async def verify_and_get_user_id_from_jwt(request):
    # Fetches JWKS from Supabase
    # Validates ES256 token
    # Returns user_id
```

## Components

### Frontend

**Supabase Client** (`apps/frontend/src/lib/supabase/client.ts`):
- Creates browser-side Supabase client
- Manages session storage
- Handles token refresh

**API Client** (`apps/frontend/src/lib/api-client.ts`):
- Automatically adds `Authorization: Bearer <token>` header
- Gets session from Supabase
- Handles 401 responses

**Auth Actions** (`apps/frontend/src/app/auth/actions.ts`):
- Server-side auth actions
- Login, logout, callback handling

### Backend

**Auth Middleware** (`backend/core/auth/auth.py`):
- `get_current_user()` - Extracts user from JWT
- `verify_role()` - RBAC role checking
- `require_admin` / `require_super_admin` - Admin guards

**JWT Utils** (`backend/core/utils/auth_utils.py`):
- `verify_and_get_user_id_from_jwt()` - Main JWT validation
- `_fetch_jwks()` - Fetches Supabase JWKS with caching
- ES256 token verification

## Token Details

- **Algorithm**: ES256 (ECDSA with P-256)
- **Issuer**: Supabase Auth
- **JWKS Endpoint**: `https://<project>.supabase.co/auth/v1/.well-known/jwks.json`
- **Session Duration**: Configurable (default 1 week)
- **Refresh**: Automatic via Supabase client

## Session Management

### Token Refresh
- Supabase client automatically refreshes tokens
- No page reload required
- Refresh token handled securely

### Logout
```typescript
await supabase.auth.signOut()
```
- Clears browser session
- Invalidates refresh token
- Redirects to login page

### Expired Sessions
- Backend returns 401 Unauthorized
- Frontend redirects to `/auth`
- User re-authenticates

## Protected Routes

### Frontend
```typescript
// HOC for protected pages
export function withAuth(Component) {
  return function AuthenticatedComponent(props) {
    const { data: session } = useSession()
    if (!session) redirect('/auth')
    return <Component {...props} />
  }
}
```

### Backend
```python
# FastAPI dependency
@router.get("/protected")
async def protected_endpoint(
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    return {"user_id": user_id}
```

## Role-Based Access Control (RBAC)

Roles stored in `user_roles` table:
- `user` - Standard user
- `admin` - Admin access
- `super_admin` - Full access

```python
# Admin-only endpoint
@router.get("/admin")
async def admin_endpoint(
    user: dict = Depends(require_admin)
):
    return {"role": user['role']}
```

## Security Considerations

1. **JWKS Caching**: Backend caches JWKS for 1 hour to reduce API calls
2. **Token Validation**: All tokens validated via Supabase JWKS
3. **HTTPS Only**: Auth only works over HTTPS
4. **CORS**: Configured for specific origins
5. **Session Storage**: Tokens stored securely in browser

## Troubleshooting

### 401 Unauthorized
- Token expired: Re-authenticate
- Invalid token: Check Supabase configuration
- Missing Authorization header: Check API client

### JWKS Fetch Failed
- Check SUPABASE_URL and SUPABASE_ANON_KEY
- Verify network connectivity
- Check JWKS cache

### Session Not Persisting
- Check browser cookies enabled
- Verify Supabase client configuration
- Check for 3rd party cookie blockers
