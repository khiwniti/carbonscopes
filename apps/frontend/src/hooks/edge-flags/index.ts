'use client';
import { BACKEND_URL } from '@/lib/api-client';
import { logger } from '@/lib/logger';

import { useQuery } from '@tanstack/react-query';

export interface IMaintenanceNotice {
  enabled: boolean;
  startTime?: string;
  endTime?: string;
}

export interface ITechnicalIssue {
  enabled: boolean;
  message?: string;
  statusUrl?: string;
  affectedServices?: string[];
  description?: string;
  estimatedResolution?: string;
  severity?: 'degraded' | 'outage' | 'maintenance';
}

export interface SystemStatusResponse {
  maintenanceNotice: IMaintenanceNotice;
  technicalIssue: ITechnicalIssue;
  updatedAt?: string;
}

async function fetchSystemStatus(): Promise<SystemStatusResponse> {
  try {
    const response = await fetch(`${BACKEND_URL}/system/status`);
    
    if (!response.ok) {
      logger.warn('Failed to fetch system status:', response.status);
      return {
        maintenanceNotice: { enabled: false },
        technicalIssue: { enabled: false },
      };
    }
    
    return await response.json();
  } catch (error) {
    logger.warn('Failed to fetch system status:', error);
    return {
      maintenanceNotice: { enabled: false },
      technicalIssue: { enabled: false },
    };
  }
}

export const systemStatusKeys = {
  all: ['system-status'] as const,
} as const;

export const useSystemStatusQuery = (options?: { enabled?: boolean }) => {
  return useQuery<SystemStatusResponse>({
    queryKey: systemStatusKeys.all,
    queryFn: fetchSystemStatus,
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000,
    refetchOnWindowFocus: true,
    refetchOnMount: 'always',
    retry: 0,
    placeholderData: {
      maintenanceNotice: { enabled: false },
      technicalIssue: { enabled: false },
    },
    ...options,
  });
};

export const useMaintenanceNoticeQuery = (options?: { enabled?: boolean }) => {
  const { data, ...rest } = useSystemStatusQuery(options);
  return {
    ...rest,
    data: data?.maintenanceNotice || { enabled: false } as IMaintenanceNotice,
  };
};

export const useTechnicalIssueQuery = (options?: { enabled?: boolean }) => {
  const { data, ...rest } = useSystemStatusQuery(options);
  return {
    ...rest,
    data: data?.technicalIssue || { enabled: false } as ITechnicalIssue,
  };
};
