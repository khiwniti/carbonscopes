'use client';
import { logger } from '@/lib/logger';

import React from 'react';
import { useOnboarding } from '@/hooks/onboarding';
import { NewOnboardingPage } from './new-onboarding-page';

interface OnboardingProviderProps {
  children: React.ReactNode;
}

export function OnboardingProvider({ children }: OnboardingProviderProps) {
  const { isOpen, completeOnboarding } = useOnboarding();

  // DISABLED: Auto-trigger onboarding after subscription
  // Onboarding is only accessible via /onboarding-demo route until it's fully ready
  // useEffect(() => {
  //   if (!subscription || !user) return;

  //   const trialStarted = searchParams?.get('trial') === 'started';
  //   const subscriptionSuccess = searchParams?.get('subscription') === 'success';
    
  //   logger.log('🚀 Onboarding Provider - Checking trigger conditions:', {
  //     trialStarted,
  //     subscriptionSuccess,
  //     subscription: subscription,
  //     shouldTrigger: shouldTriggerOnboarding(subscription)
  //   });
    
  //   if ((trialStarted || subscriptionSuccess) && shouldTriggerOnboarding(subscription)) {
  //     logger.log('✅ Triggering post-subscription onboarding');
  //     if (triggerPostSubscriptionOnboarding()) {
  //       logger.log('🎯 Starting onboarding with default steps');
  //       startOnboarding(onboardingSteps);
  //     }
  //   }
  // }, [subscription, user, searchParams, shouldTriggerOnboarding, triggerPostSubscriptionOnboarding, startOnboarding]);

  // Handle onboarding completion
  const handleOnboardingComplete = () => {
    completeOnboarding();
  };

  return (
    <>
      {children}
      {isOpen && (
        <NewOnboardingPage 
          onComplete={handleOnboardingComplete}
        />
      )}
    </>
  );
}
