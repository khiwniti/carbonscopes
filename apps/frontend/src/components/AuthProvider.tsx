'use client';

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from 'react';
import { createClient } from '@/lib/supabase/client';
import { User, Session } from '@supabase/supabase-js';
import { SupabaseClient } from '@supabase/supabase-js';
import { clearUserLocalStorage } from '@/lib/utils/clear-local-storage';
// Auth tracking moved to AuthEventTracker component (handles OAuth redirects)

type AuthContextType = {
  supabase: SupabaseClient;
  session: Session | null;
  user: User | null;
  isLoading: boolean;
  signOut: () => Promise<void>;
  signInAnonymously: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const supabase = createClient();
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const getInitialSession = async () => {
      try {
        const {
          data: { session: currentSession },
        } = await supabase.auth.getSession();
        setSession(currentSession);
        setUser(currentSession?.user ?? null);
      } catch (error) {
      } finally {
        setIsLoading(false);
      }
    };

    getInitialSession();

    const { data: authListener } = supabase.auth.onAuthStateChange(
      async (event, newSession) => {
        setSession(newSession);
        setUser(newSession?.user ?? null);

        if (isLoading) setIsLoading(false);
        switch (event) {
          case 'SIGNED_IN':
            // Auth tracking handled by AuthEventTracker component via URL params
            // Fire-and-forget fallback init for anonymous users in case the webhook missed the INSERT.
            // Gated by sessionStorage so it only fires once per browser session, not on every tab restore.
            if (newSession?.user?.is_anonymous) {
              const initKey = `anon_init_${newSession.user.id}`;
              if (!sessionStorage.getItem(initKey)) {
                sessionStorage.setItem(initKey, '1');
                import('@/lib/api-client').then(({ backendApi }) => {
                  backendApi.post('/setup/initialize-anonymous').catch(() => {});
                });
              }
            }
            break;
          case 'SIGNED_OUT':
            clearUserLocalStorage();
            break;
          case 'TOKEN_REFRESHED':
            break;
          case 'MFA_CHALLENGE_VERIFIED':
            break;
          default:
        }
      },
    );

    return () => {
      authListener?.subscription.unsubscribe();
    };
  }, [supabase]); // Removed isLoading from dependencies to prevent infinite loops

  const signOut = async () => {
    try {
      await supabase.auth.signOut();
      // Clear local storage after successful sign out
      clearUserLocalStorage();
    } catch (error) {
      console.error('❌ Error signing out:', error);
    }
  };

  const signInAnonymously = async (): Promise<void> => {
    const { error } = await supabase.auth.signInAnonymously();
    if (error) throw error;
  };

  const value = {
    supabase,
    session,
    user,
    isLoading,
    signOut,
    signInAnonymously,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    // During SSR, context doesn't exist yet - return safe defaults
    if (typeof window === 'undefined') {
      const supabase = createClient();
      return {
        supabase,
        session: null,
        user: null,
        isLoading: true,
        signOut: async () => {},
        signInAnonymously: async () => {},
      };
    }
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
