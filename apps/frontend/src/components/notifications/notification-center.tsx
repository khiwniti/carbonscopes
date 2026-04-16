'use client';

import React, { ReactNode } from 'react';
import { Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { NovuProvider, PopoverNotificationCenter, NotificationBell } from '@novu/notification-center';
import { useAuth } from '@/components/AuthProvider';
import { isStagingMode } from '@/lib/config';

interface NotificationCenterProps {
  applicationIdentifier: string;
}

// Wrapper to handle children prop type issue
interface NovuProviderWrapperProps extends React.ComponentProps<typeof NovuProvider> {
  children: ReactNode;
}

function NovuProviderWrapper(props: NovuProviderWrapperProps) {
  const { children, ...rest } = props;
  return <NovuProvider {...rest}>{children}</NovuProvider>;
}

export function NotificationCenter({ applicationIdentifier }: NotificationCenterProps) {
  const { user } = useAuth();

  if (!isStagingMode() || !user?.id || !applicationIdentifier) {
    return null;
  }

  return (
    <NovuProviderWrapper
      subscriberId={user.id}
      applicationIdentifier={applicationIdentifier}
      styles={{
        bellButton: {
          root: {
            svg: {
              fill: 'currentColor',
            },
          },
        },
      }}
    >
      <PopoverNotificationCenter colorScheme="dark">
        {({ unseenCount }) => (
          <Button
            variant="ghost"
            size="icon"
            className="relative"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5" />
            {unseenCount > 0 && (
              <Badge
                variant="destructive"
                className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
              >
                {unseenCount > 9 ? '9+' : unseenCount}
              </Badge>
            )}
          </Button>
        )}
      </PopoverNotificationCenter>
    </NovuProviderWrapper>
  );
}

export function SimpleNotificationBell() {
  const { user } = useAuth();
  const applicationIdentifier = process.env.NEXT_PUBLIC_NOVU_APP_IDENTIFIER;

  if (!user?.id || !applicationIdentifier) {
    return null;
  }

  return (
    <NovuProviderWrapper subscriberId={user.id} applicationIdentifier={applicationIdentifier}>
      <NotificationBell />
    </NovuProviderWrapper>
  );
}
