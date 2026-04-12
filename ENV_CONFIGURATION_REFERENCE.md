# Frontend Environment Configuration Reference

## Production Configuration (apps/frontend/.env.production)

### Required Variables (Must be configured)

#### Frontend URLs
```env
# Used for metadata, canonical URLs, and redirects
NEXT_PUBLIC_APP_URL=https://carbonscope-frontend-app.azurewebsites.net
NEXT_PUBLIC_URL=https://carbonscope-frontend-app.azurewebsites.net
```

#### Supabase Authentication
```env
# Frontend cannot start without these
NEXT_PUBLIC_SUPABASE_URL=https://vplbjxijbrgwskgxiukd.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<JWT token>
```

#### NextAuth Configuration
```env
# NextAuth redirects - MUST match deployed domain
NEXTAUTH_URL=https://carbonscope-frontend-app.azurewebsites.net
NEXTAUTH_SECRET=<secure random string>
```

#### Backend API
```env
# API calls to backend services
NEXT_PUBLIC_BACKEND_URL=https://carbonscope-backend-app.azurewebsites.net/v1
NEXT_PUBLIC_API_URL=https://carbonscope-backend-app.azurewebsites.net/v1
```

---

### Optional Variables (May be left empty)

#### Analytics
```env
NEXT_PUBLIC_GTM_ID=              # Google Tag Manager (empty = disabled)
NEXT_PUBLIC_POSTHOG_KEY=         # PostHog analytics (empty = disabled)
NEXT_PUBLIC_POSTHOG_HOST=        # PostHog host (empty = disabled)
NEXT_PUBLIC_SENTRY_DSN=          # Error tracking (empty = disabled)
```

#### Feature Flags & Services
```env
NEXT_PUBLIC_ENV_MODE=production
NEXT_PUBLIC_DISABLE_MOBILE_ADVERTISING=false
NEXT_PUBLIC_NOVU_APP_IDENTIFIER= # Notification service
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY= # Payment processing
NEXT_PUBLIC_PHONE_NUMBER_MANDATORY=false
NEXT_PUBLIC_VERBOSE_LOGGING=false
```

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| 404 on login | Wrong NEXTAUTH_URL | Update to deployed domain |
| Broken metadata | Wrong NEXT_PUBLIC_APP_URL | Set to Azure domain |
| Auth fails | Missing Supabase vars | Add SUPABASE_URL and ANON_KEY |
| API 401 | Backend unreachable | Check NEXT_PUBLIC_BACKEND_URL |

