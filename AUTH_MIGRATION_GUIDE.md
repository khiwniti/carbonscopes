# Authentication Migration Guide - Remove Supabase Dependency

**Date:** March 28, 2026  
**Status:** Implementation Ready  

---

## Problem

Current setup uses Supabase for authentication (Google, GitHub sign-in). Need alternatives for Azure deployment without Supabase dependency.

---

## Solution Options

### Option 1: NextAuth.js ⭐ **RECOMMENDED**

**Pros:**
- ✅ **Free & Open Source**
- ✅ Native Next.js integration
- ✅ Supports Google, GitHub, Twitter, Discord, 50+ providers
- ✅ Uses your existing PostgreSQL database
- ✅ Built-in JWT/session management
- ✅ TypeScript support
- ✅ No external service dependencies

**Cons:**
- ❌ Requires configuration
- ❌ Need to manage OAuth credentials

**Cost:** $0/month

---

### Option 2: Azure AD B2C

**Pros:**
- ✅ Native Azure integration
- ✅ Enterprise-grade security
- ✅ Supports social providers
- ✅ Custom branding

**Cons:**
- ❌ Complex setup
- ❌ Costs money after free tier
- ❌ Overkill for small apps

**Cost:** Free for first 50,000 MAU, then $0.00325/MAU

---

### Option 3: Auth0

**Pros:**
- ✅ Easy setup
- ✅ Great documentation
- ✅ Many integrations

**Cons:**
- ❌ Costs money
- ❌ External dependency

**Cost:** Free for 7,500 MAU, then $35/month+

---

### Option 4: Firebase Auth

**Pros:**
- ✅ Google-managed
- ✅ Easy integration
- ✅ Free tier

**Cons:**
- ❌ Google Cloud dependency
- ❌ Not Azure-native

**Cost:** Free for most use cases

---

## Recommended: NextAuth.js Implementation

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CarbonScope Frontend                     │
│                      (Next.js 15)                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              NextAuth.js v5                         │    │
│  │  • Google Provider                                  │    │
│  │  • GitHub Provider                                  │    │
│  │  • Email/Password (optional)                        │    │
│  │  • JWT Session Strategy                             │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Prisma Adapter                              │    │
│  │  • User table                                       │    │
│  │  • Account table                                    │    │
│  │  • Session table                                    │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  PostgreSQL Database   │
              │  (Azure/Neon/Supabase) │
              └────────────────────────┘
```

---

## Implementation Steps

### Step 1: Install Dependencies

```bash
cd apps/frontend

pnpm add next-auth@beta \
  @auth/core \
  @auth/prisma-adapter \
  @prisma/client

pnpm add -D prisma
```

### Step 2: Update Prisma Schema

Add authentication tables to `prisma/schema.prisma`:

```prisma
// prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id            String    @id @default(cuid())
  name          String?
  email         String    @unique
  emailVerified DateTime?
  image         String?
  accounts      Account[]
  sessions      Session[]
  
  // Your existing user fields
  credits       Int       @default(1000)
  role          String    @default("user")
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
  
  @@map("users")
}

model Account {
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String?
  access_token      String?
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String?
  session_state     String?

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@id([provider, providerAccountId])
  @@map("accounts")
}

model Session {
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@map("sessions")
}

model VerificationToken {
  identifier String
  token      String
  expires    DateTime

  @@id([identifier, token])
  @@map("verification_tokens")
}
```

### Step 3: Run Migrations

```bash
npx prisma migrate dev --name add_auth_tables
npx prisma generate
```

### Step 4: Get OAuth Credentials

#### Google OAuth:
1. Go to: https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID
3. Add authorized redirect URIs:
   - `http://localhost:3000/api/auth/callback/google`
   - `https://carbonscope-frontend.azurewebsites.net/api/auth/callback/google`
4. Copy **Client ID** and **Client Secret**

#### GitHub OAuth:
1. Go to: https://github.com/settings/developers
2. Create New OAuth App
3. Authorization callback URL:
   - `http://localhost:3000/api/auth/callback/github`
   - `https://carbonscope-frontend.azurewebsites.net/api/auth/callback/github`
4. Copy **Client ID** and **Client Secret**

### Step 5: Update Environment Variables

```bash
# apps/frontend/.env.local

# Database
DATABASE_URL="postgresql://user:pass@host:5432/carbonscope_db"

# NextAuth.js
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-super-secret-key-min-32-chars"

# Google OAuth
GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-google-client-secret"

# GitHub OAuth
GITHUB_CLIENT_ID="your-github-client-id"
GITHUB_CLIENT_SECRET="your-github-client-secret"
```

Generate `NEXTAUTH_SECRET`:
```bash
openssl rand -base64 32
```

### Step 6: Create Auth Configuration

Create `apps/frontend/src/lib/auth.ts`:

```typescript
import NextAuth, { NextAuthConfig } from "next-auth";
import Google from "next-auth/providers/google";
import GitHub from "next-auth/providers/github";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

export const authConfig: NextAuthConfig = {
  adapter: PrismaAdapter(prisma),
  
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline",
          response_type: "code"
        }
      }
    }),
    
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
  ],
  
  pages: {
    signIn: "/auth",
    error: "/auth/error",
  },
  
  callbacks: {
    async session({ session, user }) {
      if (session.user) {
        session.user.id = user.id;
        // Add custom fields
        session.user.role = user.role;
        session.user.credits = user.credits;
      }
      return session;
    },
    
    async redirect({ url, baseUrl }) {
      // Redirect to dashboard after sign in
      if (url.startsWith("/")) return `${baseUrl}${url}`;
      else if (new URL(url).origin === baseUrl) return url;
      return `${baseUrl}/dashboard`;
    },
  },
  
  session: {
    strategy: "database",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  
  debug: process.env.NODE_ENV === "development",
};

export const { handlers, auth, signIn, signOut } = NextAuth(authConfig);
```

### Step 7: Create API Route

Create `apps/frontend/src/app/api/auth/[...nextauth]/route.ts`:

```typescript
import { handlers } from "@/lib/auth";

export const { GET, POST } = handlers;
```

### Step 8: Update Auth Provider

Replace Supabase AuthProvider with NextAuth:

```typescript
// apps/frontend/src/components/providers/auth-provider.tsx

"use client";

import { SessionProvider } from "next-auth/react";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return <SessionProvider>{children}</SessionProvider>;
}
```

### Step 9: Update Root Layout

```typescript
// apps/frontend/src/app/layout.tsx

import { AuthProvider } from "@/components/providers/auth-provider";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

### Step 10: Update Auth Page

```typescript
// apps/frontend/src/app/auth/page.tsx

"use client";

import { signIn } from "next-auth/react";
import { useState } from "react";
import { CarbonScopeLogoSimple } from "@/components/brand/carbonscope-logo-simple";

export default function AuthPage() {
  const [isLoading, setIsLoading] = useState<string | null>(null);

  const handleSignIn = async (provider: "google" | "github") => {
    setIsLoading(provider);
    try {
      await signIn(provider, { callbackUrl: "/dashboard" });
    } catch (error) {
      console.error("Sign in error:", error);
      setIsLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B1120] flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        {/* Logo */}
        <div className="flex justify-center">
          <CarbonScopeLogoSimple size={64} />
        </div>

        {/* Title */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white">
            Sign in to <span className="text-emerald-500">CarbonScope</span>
          </h1>
          <p className="mt-2 text-gray-400">
            Choose your preferred sign-in method
          </p>
        </div>

        {/* Sign In Buttons */}
        <div className="space-y-3">
          {/* Google Sign In */}
          <button
            onClick={() => handleSignIn("google")}
            disabled={isLoading !== null}
            className="w-full flex items-center justify-center gap-3 px-6 py-3 bg-white hover:bg-gray-50 text-gray-900 rounded-lg transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading === "google" ? (
              <div className="w-5 h-5 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
            ) : (
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
            )}
            <span className="font-medium">Continue with Google</span>
          </button>

          {/* GitHub Sign In */}
          <button
            onClick={() => handleSignIn("github")}
            disabled={isLoading !== null}
            className="w-full flex items-center justify-center gap-3 px-6 py-3 bg-gray-900 hover:bg-gray-800 text-white rounded-lg transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading === "github" ? (
              <div className="w-5 h-5 border-2 border-gray-600 border-t-white rounded-full animate-spin" />
            ) : (
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
              </svg>
            )}
            <span className="font-medium">Continue with GitHub</span>
          </button>
        </div>

        {/* Terms */}
        <p className="text-center text-sm text-gray-400">
          By signing in, you agree to our{" "}
          <a href="/legal/terms" className="text-emerald-500 hover:underline">
            Terms of Service
          </a>{" "}
          and{" "}
          <a href="/legal/privacy" className="text-emerald-500 hover:underline">
            Privacy Policy
          </a>
        </p>
      </div>
    </div>
  );
}
```

### Step 11: Create Auth Hooks

```typescript
// apps/frontend/src/hooks/use-auth.ts

"use client";

import { useSession, signIn, signOut } from "next-auth/react";

export function useAuth() {
  const { data: session, status } = useSession();

  return {
    user: session?.user,
    isLoading: status === "loading",
    isAuthenticated: status === "authenticated",
    signIn,
    signOut,
  };
}
```

### Step 12: Protect Routes with Middleware

```typescript
// apps/frontend/src/middleware.ts

import { auth } from "@/lib/auth";
import { NextResponse } from "next/server";

export default auth((req) => {
  const isLoggedIn = !!req.auth;
  const isAuthPage = req.nextUrl.pathname.startsWith("/auth");
  const isProtectedRoute = 
    req.nextUrl.pathname.startsWith("/dashboard") ||
    req.nextUrl.pathname.startsWith("/agents") ||
    req.nextUrl.pathname.startsWith("/projects");

  if (isProtectedRoute && !isLoggedIn) {
    return NextResponse.redirect(new URL("/auth", req.url));
  }

  if (isAuthPage && isLoggedIn) {
    return NextResponse.redirect(new URL("/dashboard", req.url));
  }

  return NextResponse.next();
});

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/agents/:path*",
    "/projects/:path*",
    "/settings/:path*",
    "/auth/:path*",
  ],
};
```

---

## Migration Checklist

### Pre-Migration

- [ ] Backup existing user data from Supabase
- [ ] Export OAuth credentials
- [ ] Document current auth flow

### Installation

- [ ] Install NextAuth.js dependencies
- [ ] Update Prisma schema
- [ ] Run database migrations
- [ ] Generate Prisma client

### Configuration

- [ ] Get Google OAuth credentials
- [ ] Get GitHub OAuth credentials
- [ ] Generate NEXTAUTH_SECRET
- [ ] Update environment variables

### Code Changes

- [ ] Create auth configuration (`lib/auth.ts`)
- [ ] Create API route (`api/auth/[...nextauth]/route.ts`)
- [ ] Update AuthProvider component
- [ ] Update auth page UI
- [ ] Create auth hooks
- [ ] Add middleware for route protection

### Testing

- [ ] Test Google sign-in (local)
- [ ] Test GitHub sign-in (local)
- [ ] Test sign-out
- [ ] Test protected routes
- [ ] Test session persistence

### Production Deployment

- [ ] Update OAuth redirect URLs for production
- [ ] Set production environment variables in Azure
- [ ] Test authentication in production
- [ ] Monitor for errors

### Cleanup

- [ ] Remove Supabase dependencies
- [ ] Remove old auth code
- [ ] Update documentation

---

## Cost Comparison

| Service | Free Tier | Paid Plans |
|---------|-----------|------------|
| **NextAuth.js** | ✅ Unlimited | $0/month (self-hosted) |
| **Supabase Auth** | 50,000 MAU | $25/month + usage |
| **Auth0** | 7,500 MAU | $35/month+ |
| **Azure AD B2C** | 50,000 MAU | $0.00325/MAU |
| **Firebase Auth** | Unlimited (mostly) | Usage-based |

**Winner:** NextAuth.js ($0/month, no limits)

---

## Security Considerations

### ✅ NextAuth.js Security Features:

1. **CSRF Protection** - Built-in
2. **XSS Protection** - Secure cookie handling
3. **Session Management** - Automatic refresh
4. **JWT Signing** - HS256/RS256 support
5. **Database Sessions** - Optional
6. **Secure Cookies** - httpOnly, secure flags
7. **OAuth State Parameter** - PKCE support

### 🔒 Best Practices:

- Use strong `NEXTAUTH_SECRET` (32+ chars)
- Enable HTTPS in production
- Set secure cookie flags
- Implement rate limiting
- Use database sessions for sensitive apps
- Rotate OAuth secrets regularly

---

## Troubleshooting

### Issue: "Invalid callback URL"
**Solution:** Check OAuth redirect URIs match exactly (http vs https, trailing slash)

### Issue: "Session not persisting"
**Solution:** Check cookie settings, ensure DATABASE_URL is correct

### Issue: "Provider not configured"
**Solution:** Verify GOOGLE_CLIENT_ID and GITHUB_CLIENT_ID are set

### Issue: "Database connection failed"
**Solution:** Run `npx prisma generate` and check DATABASE_URL

---

## Additional Providers

Want more sign-in options? Add these providers:

```typescript
// lib/auth.ts

import Discord from "next-auth/providers/discord";
import Twitter from "next-auth/providers/twitter";
import Microsoft from "next-auth/providers/microsoft";

providers: [
  Google({ ... }),
  GitHub({ ... }),
  Discord({
    clientId: process.env.DISCORD_CLIENT_ID!,
    clientSecret: process.env.DISCORD_CLIENT_SECRET!,
  }),
  Twitter({
    clientId: process.env.TWITTER_CLIENT_ID!,
    clientSecret: process.env.TWITTER_CLIENT_SECRET!,
    version: "2.0",
  }),
  Microsoft({
    clientId: process.env.MICROSOFT_CLIENT_ID!,
    clientSecret: process.env.MICROSOFT_CLIENT_SECRET!,
  }),
],
```

---

## Next Steps

1. **Run the migration script** (see below)
2. **Test authentication locally**
3. **Update Azure environment variables**
4. **Deploy to production**
5. **Monitor for issues**

---

## Quick Start Command

```bash
# Install dependencies
cd apps/frontend && pnpm add next-auth@beta @auth/core @auth/prisma-adapter

# Generate secret
openssl rand -base64 32

# Update .env.local with OAuth credentials

# Run migrations
npx prisma migrate dev --name add_auth_tables

# Start dev server
pnpm dev

# Test: http://localhost:3000/auth
```

---

## Support

- **NextAuth.js Docs:** https://authjs.dev
- **Discord:** https://discord.gg/nextauth
- **GitHub:** https://github.com/nextauthjs/next-auth

---

**Status:** ✅ Ready to implement  
**Estimated Time:** 2-3 hours  
**Difficulty:** Medium  
**Cost Savings:** $25-35/month vs paid alternatives
