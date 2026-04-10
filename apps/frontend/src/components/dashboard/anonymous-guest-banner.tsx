'use client';

import { useState, useEffect } from 'react';
import { UserCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/components/AuthProvider';
import { usePathname } from 'next/navigation';

export function AnonymousGuestBanner() {
  const { user, isLoading } = useAuth();
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const isAnonymous = !isLoading && !!user?.is_anonymous;
  const isDashboard = pathname?.startsWith('/dashboard') ?? false;
  const shouldShow = mounted && isAnonymous && isDashboard;

  const handleSaveChats = () => {
    window.location.href = `/auth?returnUrl=${encodeURIComponent(pathname ?? '/dashboard')}&mode=signup`;
  };

  if (!shouldShow) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.2, ease: 'easeOut' }}
        className="absolute top-0 left-0 right-0 z-50 pointer-events-auto"
      >
        <div className="border-b border-amber-500/20 bg-amber-950/30 backdrop-blur-md">
          <div className="px-4 py-2">
            <div className="flex items-center justify-center gap-3 sm:gap-4">
              <div className="flex items-center gap-2">
                <UserCircle className="h-3.5 w-3.5 shrink-0 text-amber-400" />
                <span className="text-xs sm:text-sm font-medium text-foreground">
                  Your chats are temporary.
                  <span className="text-muted-foreground mx-1.5 hidden sm:inline">·</span>
                  <span className="text-muted-foreground hidden sm:inline">Sign in to save them permanently.</span>
                </span>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={handleSaveChats}
                className="h-6 shrink-0 px-2.5 text-xs font-medium border-amber-500/40 text-amber-300 hover:bg-amber-500/10 hover:text-amber-200"
              >
                Save my chats
              </Button>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
