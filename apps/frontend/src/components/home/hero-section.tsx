'use client';

import { useState, useEffect, lazy, Suspense } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/components/AuthProvider';
import { createClient } from '@/lib/supabase/client';
import { useIsMobile } from '@/hooks/utils';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogOverlay,
} from '@/components/ui/dialog';
import { useTranslations } from 'next-intl';
import { trackCtaSignup } from '@/lib/analytics/gtm';
import { useAgentStartInput } from '@/hooks/dashboard';
import { ChatInput } from '@/components/thread/chat-input/chat-input';
import { DynamicGreeting } from '@/components/ui/dynamic-greeting';

// Lazy load heavy components
const CarbonScopeModesPanel = lazy(() => 
  import('@/components/dashboard/carbonscope-modes-panel').then(mod => ({ default: mod.CarbonScopeModesPanel }))
);
const GoogleSignIn = lazy(() => import('@/components/GoogleSignIn'));

const BlurredDialogOverlay = () => (
  <DialogOverlay className="bg-black/80 backdrop-blur-md" />
);

export function HeroSection() {
  const t = useTranslations('dashboard');
  const tAuth = useTranslations('auth');
  const isMobile = useIsMobile();
  const router = useRouter();
  const { user, isLoading, signInAnonymously } = useAuth();
  const [isAnonymousLoading, setIsAnonymousLoading] = useState(false);
  
  const [authDialogOpen, setAuthDialogOpen] = useState(false);
  
  // Close auth dialog and redirect when user logs in
  useEffect(() => {
    if (authDialogOpen && user && !isLoading) {
      setAuthDialogOpen(false);
      router.push('/dashboard');
    }
  }, [user, isLoading, authDialogOpen, router]);
  
  // Sign in anonymously then retry — no email/password needed
  const handleAuthRequired = async (pendingMessage: string) => {
    trackCtaSignup();
    try {
      const supabase = createClient();
      const { error } = await supabase.auth.signInAnonymously();
      if (error) {
        // Fall back to auth dialog if anonymous sign-in fails
        setAuthDialogOpen(true);
      }
      // Auth state change will re-trigger submission via autoSubmit
    } catch {
      setAuthDialogOpen(true);
    }
  };

  const handleContinueAsGuest = async () => {
    setIsAnonymousLoading(true);
    setAuthDialogOpen(false);
    try {
      await signInAnonymously();
      // Auth state change triggers the useEffect above → router.push('/dashboard')
    } catch {
      setAuthDialogOpen(true);
    } finally {
      setIsAnonymousLoading(false);
    }
  };

  // Use the agent start input hook for state management (same as dashboard)
  const {
    inputValue,
    setInputValue,
    isSubmitting,
    isRedirecting,
    chatInputRef,
    selectedAgentId,
    setSelectedAgent,
    selectedMode,
    selectedCharts,
    selectedOutputFormat,
    selectedTemplate,
    setSelectedMode,
    setSelectedCharts,
    setSelectedOutputFormat,
    setSelectedTemplate,
    handleSubmit,
  } = useAgentStartInput({
    redirectOnError: '/',
    requireAuth: true,
    onAuthRequired: handleAuthRequired,
    enableAutoSubmit: true,
    logPrefix: '[HeroSection]',
  });
  
  return (
    <section id="hero" style={{
      width: '100%',
      height: '100dvh',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '100%',
        overflow: 'hidden',
        position: 'relative'
      }}>

        {/* Main content area - greeting and modes centered */}
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          zIndex: 10
        }}>
          {/* Centered content: Greeting + Subtitle + Modes
              - Mobile: shifted up with pb-28 to account for chat input and feel more balanced
              - Desktop: true center with no offset */}
          <div style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '0 1rem',
            paddingBottom: isMobile ? '7rem' : 0,
            pointerEvents: 'none',
            zIndex: 10
          }}>
            <div style={{
              width: '100%',
              maxWidth: '48rem',
              margin: '0 auto',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              pointerEvents: 'auto',
              position: 'relative',
              zIndex: 10
            }}>
              {/* Greeting */}
              <div className="animate-in fade-in-0 slide-in-from-bottom-4 duration-500 fill-mode-both" style={{
                fontFamily: "'Instrument Serif', Georgia, serif",
                fontSize: 'clamp(1.5rem, 5vw, 2.5rem)',
                lineHeight: 1.1,
                fontWeight: 700
              }}>
                <DynamicGreeting />
              </div>

              {/* Subtitle */}
              <p className="animate-in fade-in-0 slide-in-from-bottom-4 duration-500 delay-75 fill-mode-both" style={{
                fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
                color: '#64748B',
                fontSize: '0.875rem',
                marginTop: isMobile ? '0.5rem' : '0.75rem'
              }}>
                {t('modeSubtitle')}
              </p>
              
              {/* Modes Panel */}
              <div className="animate-in fade-in-0 slide-in-from-bottom-4 duration-500 delay-150 fill-mode-both" style={{
                marginTop: isMobile ? '1.5rem' : '2rem',
                width: '100%'
              }}>
                <Suspense fallback={<div style={{ height: '3rem', background: 'rgba(52, 211, 153, 0.1)', borderRadius: '0.5rem' }} className="animate-pulse" />}>
<CarbonScopeModesPanel
                    selectedMode={selectedMode}
                    onModeSelect={setSelectedMode}
                    onSelectPrompt={setInputValue}
                    isMobile={isMobile}
                    selectedCharts={selectedCharts}
                    onChartsChange={setSelectedCharts}
                    selectedOutputFormat={selectedOutputFormat}
                    onOutputFormatChange={setSelectedOutputFormat}
                    selectedTemplate={selectedTemplate}
                    onTemplateChange={setSelectedTemplate}
                    isFreeTier={true}
                    onUpgradeClick={() => {}}
                  />
                </Suspense>
              </div>
            </div>
          </div>

          {/* Chat Input - fixed at bottom
              - Mobile: safe area padding for iOS home indicator */}
          <div className="animate-in fade-in-0 slide-in-from-bottom-4 duration-500 delay-100 fill-mode-both" style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            padding: isMobile ? '0.75rem' : '1rem',
            paddingBottom: isMobile ? 'max(0.75rem, env(safe-area-inset-bottom))' : '1rem',
            zIndex: 10
          }}>
            <div style={{
              width: '100%',
              maxWidth: '48rem',
              margin: '0 auto'
            }}>
              <ChatInput
                ref={chatInputRef}
                onSubmit={handleSubmit}
                placeholder={t('describeWhatYouNeed')}
                loading={isSubmitting || isRedirecting}
                disabled={isSubmitting}
                value={inputValue}
                onChange={setInputValue}
                isLoggedIn={!!user}
                selectedAgentId={selectedAgentId}
                onAgentSelect={setSelectedAgent}
                autoFocus={false}
                enableAdvancedConfig={false}
                selectedMode={selectedMode}
                onModeDeselect={() => setSelectedMode(null)}
                animatePlaceholder={true}
                hideAttachments={false}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Auth Dialog */}
      <Dialog open={authDialogOpen} onOpenChange={setAuthDialogOpen}>
        <BlurredDialogOverlay />
        <DialogContent className="sm:max-w-md rounded-xl bg-background border border-border">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <DialogTitle className="text-xl font-medium">
                {tAuth('signInToContinue')}
              </DialogTitle>
            </div>
            <DialogDescription className="text-muted-foreground">
              {tAuth('signInOrCreateAccountToTalk')}
            </DialogDescription>
          </DialogHeader>

          <div className="w-full space-y-3 mt-8">
            <Suspense fallback={<div className="h-12 bg-muted/20 rounded-full animate-pulse" />}>
              <GoogleSignIn returnUrl="/dashboard" />
            </Suspense>
          </div>

          <div className="relative my-2">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-3 bg-background text-muted-foreground font-medium">
                {tAuth('orContinueWithEmail')}
              </span>
            </div>
          </div>

          <div className="space-y-3">
            <Link
              href={`/auth?returnUrl=${encodeURIComponent('/dashboard')}`}
              className="flex h-12 items-center justify-center w-full text-center rounded-full bg-primary text-primary-foreground hover:bg-primary/90 transition-all shadow-sm font-medium"
              onClick={() => {
                trackCtaSignup();
                setAuthDialogOpen(false);
              }}
            >
              {tAuth('signInWithEmail')}
            </Link>

            <Link
              href={`/auth?mode=signup&returnUrl=${encodeURIComponent('/dashboard')}`}
              className="flex h-12 items-center justify-center w-full text-center rounded-full border border-border bg-background hover:bg-accent/50 transition-all font-medium"
              onClick={() => {
                trackCtaSignup();
                setAuthDialogOpen(false);
              }}
            >
              {tAuth('createNewAccount')}
            </Link>
          </div>

          <div className="relative my-2">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-3 bg-background text-muted-foreground font-medium">
                {tAuth('or')}
              </span>
            </div>
          </div>

          <button
            type="button"
            disabled={isAnonymousLoading}
            onClick={handleContinueAsGuest}
            className="flex h-12 items-center justify-center w-full text-center rounded-full border border-border/50 bg-transparent hover:bg-accent/30 transition-all font-medium text-muted-foreground hover:text-foreground text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isAnonymousLoading ? (
              <span className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            ) : (
              tAuth('continueAsGuest')
            )}
          </button>

          <div className="mt-8 text-center text-[13px] text-muted-foreground leading-relaxed">
            {tAuth('byContinuingYouAgreeSimple')}{' '}
            <a href="https://www.carbonscope.ai/legal?tab=terms" target="_blank" rel="noopener noreferrer" className="text-foreground/70 hover:text-foreground underline underline-offset-2 transition-colors">
              {tAuth('termsOfService')}
            </a>{' '}
            and{' '}
            <a href="https://www.carbonscope.ai/legal?tab=privacy" target="_blank" rel="noopener noreferrer" className="text-foreground/70 hover:text-foreground underline underline-offset-2 transition-colors">
              {tAuth('privacyPolicy')}
            </a>
          </div>
        </DialogContent>
      </Dialog>
    </section>
  );
}
