#!/bin/bash

################################################################################
# CarbonScope Authentication Migration Script
# Migrate from Supabase Auth to NextAuth.js
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

clear
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     CarbonScope Authentication Migration                      ║"
echo "║     From: Supabase Auth → To: NextAuth.js                     ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

print_info "This script will:"
echo "  1. Install NextAuth.js dependencies"
echo "  2. Create Prisma auth schema"
echo "  3. Generate auth configuration files"
echo "  4. Update auth components"
echo "  5. Create migration guide"
echo ""

read -p "$(echo -e ${YELLOW}Continue with migration? [y/N]: ${NC})" -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Migration cancelled"
    exit 0
fi

# Navigate to frontend
cd apps/frontend

print_header "Step 1: Installing Dependencies"

print_info "Installing NextAuth.js..."
pnpm add next-auth@beta @auth/core @auth/prisma-adapter @prisma/client
print_success "Dependencies installed"

print_header "Step 2: Setting Up Prisma"

# Create prisma directory if it doesn't exist
mkdir -p prisma

# Create auth schema
print_info "Creating Prisma auth schema..."
cat > prisma/schema.prisma << 'EOF'
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
  
  // CarbonScope fields
  credits       Int       @default(1000)
  role          String    @default("user")
  
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  
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
EOF

print_success "Prisma schema created"

print_header "Step 3: Creating Auth Configuration"

# Create lib directory
mkdir -p src/lib

# Create auth.ts
print_info "Creating auth configuration..."
cat > src/lib/auth.ts << 'EOF'
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
        // @ts-ignore - Add custom fields
        session.user.role = user.role;
        // @ts-ignore
        session.user.credits = user.credits;
      }
      return session;
    },
    
    async redirect({ url, baseUrl }) {
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
EOF

print_success "Auth configuration created"

print_header "Step 4: Creating API Route"

# Create API route
mkdir -p src/app/api/auth/\[...nextauth\]
cat > src/app/api/auth/\[...nextauth\]/route.ts << 'EOF'
import { handlers } from "@/lib/auth";

export const { GET, POST } = handlers;
EOF

print_success "API route created"

print_header "Step 5: Creating Auth Provider"

mkdir -p src/components/providers
cat > src/components/providers/auth-provider.tsx << 'EOF'
"use client";

import { SessionProvider } from "next-auth/react";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return <SessionProvider>{children}</SessionProvider>;
}
EOF

print_success "Auth provider created"

print_header "Step 6: Creating Auth Hook"

mkdir -p src/hooks
cat > src/hooks/use-auth.ts << 'EOF'
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
EOF

print_success "Auth hook created"

print_header "Step 7: Creating Middleware"

cat > src/middleware.ts << 'EOF'
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
EOF

print_success "Middleware created"

print_header "Step 8: Generating NEXTAUTH_SECRET"

NEXTAUTH_SECRET=$(openssl rand -base64 32)
print_success "Generated NEXTAUTH_SECRET"

print_header "Step 9: Environment Variables"

echo ""
echo "Add these to your .env.local file:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
cat << EOF
# Database
DATABASE_URL="postgresql://user:pass@host:5432/carbonscope_db"

# NextAuth.js
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="${NEXTAUTH_SECRET}"

# Google OAuth (get from: https://console.cloud.google.com/apis/credentials)
GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-google-client-secret"

# GitHub OAuth (get from: https://github.com/settings/developers)
GITHUB_CLIENT_ID="your-github-client-id"
GITHUB_CLIENT_SECRET="your-github-client-secret"
EOF
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

print_header "Step 10: OAuth Setup Instructions"

echo ""
echo "📱 GOOGLE OAUTH SETUP:"
echo "  1. Go to: https://console.cloud.google.com/apis/credentials"
echo "  2. Create OAuth 2.0 Client ID"
echo "  3. Add redirect URIs:"
echo "     • http://localhost:3000/api/auth/callback/google"
echo "     • https://your-domain.com/api/auth/callback/google"
echo "  4. Copy Client ID and Client Secret"
echo ""
echo "🐙 GITHUB OAUTH SETUP:"
echo "  1. Go to: https://github.com/settings/developers"
echo "  2. Create New OAuth App"
echo "  3. Set callback URL:"
echo "     • http://localhost:3000/api/auth/callback/github"
echo "  4. Copy Client ID and Client Secret"
echo ""

print_header "Next Steps"

echo ""
echo "1. Update .env.local with OAuth credentials"
echo ""
echo "2. Run database migrations:"
echo "   npx prisma migrate dev --name add_auth_tables"
echo "   npx prisma generate"
echo ""
echo "3. Update your layout to use the new AuthProvider"
echo ""
echo "4. Test authentication:"
echo "   pnpm dev"
echo "   Visit: http://localhost:3000/auth"
echo ""
echo "5. Read full guide:"
echo "   cat ../../AUTH_MIGRATION_GUIDE.md"
echo ""

print_success "Migration setup complete!"
echo ""
echo -e "${GREEN}✓ NextAuth.js is now configured for CarbonScope${NC}"
echo ""
