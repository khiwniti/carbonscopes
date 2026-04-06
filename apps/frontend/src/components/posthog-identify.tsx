'use client';

import { useEffect } from 'react';
import { createClient } from '@/lib/supabase/client';
import { initPostHog, identify, reset, isPostHogAvailable } from '@/lib/posthog';

export const PostHogIdentify = () => {
  useEffect(() => {
    // Initialize PostHog on mount (safe to call multiple times)
    initPostHog();
    
    // If PostHog is not available, don't set up listeners
    if (!isPostHogAvailable()) return;

    const supabase = createClient();
    const listener = supabase.auth.onAuthStateChange((_, session) => {
      if (session) {
        identify(session.user.id, { email: session.user.email });
      } else {
        reset();
      }
    });

    return () => {
      listener.data.subscription.unsubscribe();
    };
  }, []);

  return null;
};
