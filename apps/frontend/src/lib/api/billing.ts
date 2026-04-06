/**
 * BILLING DISABLED - All functions return unlimited/free access
 * This file has been modified to disable all billing functionality
 */

import { logger } from '@/lib/logger';

// =============================================================================
// UNIFIED ACCOUNT STATE - Returns unlimited free access
// =============================================================================

export interface AccountState {
  credits: {
    total: number;
    daily: number;
    monthly: number;
    extra: number;
    can_run: boolean;
    daily_refresh: {
      enabled: boolean;
      daily_amount: number;
      refresh_interval_hours: number;
      last_refresh?: string;
      next_refresh_at?: string;
      seconds_until_refresh?: number;
    } | null;
  };
  subscription: {
    tier_key: string;
    tier_display_name: string;
    status: string;
    billing_period: 'monthly' | 'yearly' | 'yearly_commitment' | null;
    provider: 'stripe' | 'revenuecat' | 'local';
    subscription_id: string | null;
    current_period_end: number | null;
    cancel_at_period_end: boolean;
    is_trial: boolean;
    trial_status: string | null;
    trial_ends_at: string | null;
    is_cancelled: boolean;
    cancellation_effective_date: string | null;
    has_scheduled_change: boolean;
    scheduled_change: {
      type: 'downgrade';
      current_tier: {
        name: string;
        display_name: string;
        monthly_credits?: number;
      };
      target_tier: {
        name: string;
        display_name: string;
        monthly_credits?: number;
      };
      effective_date: string;
    } | null;
    commitment: {
      has_commitment: boolean;
      can_cancel: boolean;
      commitment_type?: string | null;
      months_remaining?: number | null;
      commitment_end_date?: string | null;
    };
    can_purchase_credits: boolean;
  };
  models: Array<{
    id: string;
    name: string;
    provider: string;
    allowed: boolean;
    context_window: number;
    capabilities: string[];
    priority: number;
    recommended: boolean;
  }>;
  limits: {
    projects: {
      current: number;
      max: number;
      can_create: boolean;
      tier_name: string;
    };
    threads: {
      current: number;
      max: number;
      can_create: boolean;
      tier_name: string;
    };
    concurrent_runs: {
      running_count: number;
      limit: number;
      can_start: boolean;
      tier_name: string;
    };
    ai_worker_count: {
      current_count: number;
      limit: number;
      can_create: boolean;
      tier_name: string;
    };
    custom_mcp_count: {
      current_count: number;
      limit: number;
      can_create: boolean;
      tier_name: string;
    };
    trigger_count: {
      scheduled: {
        current_count: number;
        limit: number;
        can_create: boolean;
      };
      app: {
        current_count: number;
        limit: number;
        can_create: boolean;
      };
      tier_name: string;
    };
  };
  tier: {
    name: string;
    display_name: string;
    monthly_credits: number;
    can_purchase_credits: boolean;
  };
  _cache?: {
    cached: boolean;
    ttl_seconds?: number;
    local_mode?: boolean;
  };
}

// =============================================================================
// UNLIMITED FREE ACCOUNT STATE - Billing disabled
// =============================================================================

const UNLIMITED_ACCOUNT_STATE: AccountState = {
  credits: {
    total: 999999,
    daily: 999999,
    monthly: 999999,
    extra: 0,
    can_run: true,
    daily_refresh: null,
  },
  subscription: {
    tier_key: 'unlimited',
    tier_display_name: 'Unlimited (Billing Disabled)',
    status: 'active',
    billing_period: null,
    provider: 'local',
    subscription_id: null,
    current_period_end: null,
    cancel_at_period_end: false,
    is_trial: false,
    trial_status: null,
    trial_ends_at: null,
    is_cancelled: false,
    cancellation_effective_date: null,
    has_scheduled_change: false,
    scheduled_change: null,
    commitment: {
      has_commitment: false,
      can_cancel: true,
      commitment_type: null,
      months_remaining: null,
      commitment_end_date: null,
    },
    can_purchase_credits: false,
  },
  models: [
    {
      id: 'claude-sonnet-4-20250514',
      name: 'Claude Sonnet 4',
      provider: 'anthropic',
      allowed: true,
      context_window: 200000,
      capabilities: ['text', 'vision', 'tools'],
      priority: 1,
      recommended: true,
    },
    {
      id: 'gpt-4o',
      name: 'GPT-4o',
      provider: 'openai',
      allowed: true,
      context_window: 128000,
      capabilities: ['text', 'vision', 'tools'],
      priority: 2,
      recommended: false,
    },
  ],
  limits: {
    projects: {
      current: 0,
      max: 999999,
      can_create: true,
      tier_name: 'unlimited'
    },
    threads: {
      current: 0,
      max: 999999,
      can_create: true,
      tier_name: 'unlimited'
    },
    concurrent_runs: {
      running_count: 0,
      limit: 999999,
      can_start: true,
      tier_name: 'unlimited'
    },
    ai_worker_count: {
      current_count: 0,
      limit: 999999,
      can_create: true,
      tier_name: 'unlimited'
    },
    custom_mcp_count: {
      current_count: 0,
      limit: 999999,
      can_create: true,
      tier_name: 'unlimited'
    },
    trigger_count: {
      scheduled: {
        current_count: 0,
        limit: 999999,
        can_create: true
      },
      app: {
        current_count: 0,
        limit: 999999,
        can_create: true
      },
      tier_name: 'unlimited'
    }
  },
  tier: {
    name: 'unlimited',
    display_name: 'Unlimited (Billing Disabled)',
    monthly_credits: 999999,
    can_purchase_credits: false,
  },
  _cache: {
    cached: true,
    local_mode: true,
  }
};

// =============================================================================
// MOCK TYPES - Keep for compatibility
// =============================================================================

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  model: string;
  thread_id?: string;
  message_id?: string;
}

export interface DeductResult {
  success: boolean;
  cost: number;
  new_balance: number;
  transaction_id?: string;
}

export interface CreateCheckoutSessionRequest {
  tier_key: string;
  success_url: string;
  cancel_url: string;
  referral_id?: string;
  commitment_type?: 'monthly' | 'yearly' | 'yearly_commitment';
  locale?: string;
}

export interface CreateCheckoutSessionResponse {
  status: string;
  message?: string;
  checkout_url?: string;
  url?: string;
}

export interface CreatePortalSessionRequest {
  return_url: string;
}

export interface CreatePortalSessionResponse {
  portal_url: string;
}

export interface PurchaseCreditsRequest {
  amount: number;
  success_url: string;
  cancel_url: string;
}

export interface PurchaseCreditsResponse {
  checkout_url: string;
}

export interface CancelSubscriptionRequest {
  feedback?: string;
}

export interface CancelSubscriptionResponse {
  success: boolean;
  cancel_at: number;
  message: string;
}

export interface ReactivateSubscriptionResponse {
  success: boolean;
  message: string;
}

export interface ScheduleDowngradeRequest {
  target_tier_key: string;
  commitment_type?: 'monthly' | 'yearly' | 'yearly_commitment';
}

export interface ScheduleDowngradeResponse {
  success: boolean;
  message: string;
  scheduled_date: string;
  current_tier: { name: string; display_name: string; monthly_credits: number; };
  target_tier: { name: string; display_name: string; monthly_credits: number; };
  billing_change: boolean;
  current_billing_period: string;
  target_billing_period: string;
  change_description: string;
}

export interface CancelScheduledChangeResponse {
  success: boolean;
  message: string;
}

export interface Transaction {
  id: string;
  user_id: string;
  type: 'credit' | 'debit';
  amount: number;
  description: string;
  reference_id?: string;
  reference_type?: string;
  created_at: string;
}

export interface UsageHistory {
  daily_usage: Record<string, { credits: number; debits: number; count: number; }>;
  total_period_usage: number;
  total_period_credits: number;
}

export interface TrialStatus {
  has_trial: boolean;
  trial_status?: string;
  can_start_trial?: boolean;
  message?: string;
}

export interface TrialStartRequest {
  success_url: string;
  cancel_url: string;
}

export interface TrialStartResponse {
  checkout_url: string;
  session_id: string;
}

export interface TrialCheckoutRequest {
  success_url: string;
  cancel_url: string;
}

export interface TrialCheckoutResponse {
  checkout_url: string;
  session_id: string;
}

export interface CheckoutSessionDetails {
  session_id: string;
  amount_total: number;
  amount_subtotal: number;
  amount_discount: number;
  amount_tax: number;
  currency: string;
  coupon_id: string | null;
  coupon_name: string | null;
  promotion_code: string | null;
  balance_transaction_id: string | null;
  status: string;
  payment_status: string;
}

export interface CreateInlineCheckoutRequest {
  tier_key: string;
  billing_period: 'monthly' | 'yearly';
  promo_code?: string;
}

export interface CreateInlineCheckoutResponse {
  client_secret?: string;
  subscription_id: string;
  tier_key: string;
  amount?: number;
  currency?: string;
  no_payment_required?: boolean;
  upgraded?: boolean;
  previous_tier?: string;
  credits_granted?: number;
  message?: string;
}

export interface ConfirmInlineCheckoutRequest {
  subscription_id: string;
  tier_key: string;
  payment_intent_id?: string;
}

export interface ConfirmInlineCheckoutResponse {
  success: boolean;
  tier: string;
  message: string;
}

// =============================================================================
// BILLING API - ALL DISABLED, RETURNS MOCK DATA
// =============================================================================

export const billingApi = {
  async getAccountState(_skipCache = false): Promise<AccountState> {
    logger.debug('[Billing] Billing disabled - returning unlimited access');
    return UNLIMITED_ACCOUNT_STATE;
  },

  async deductTokenUsage(_usage: TokenUsage): Promise<DeductResult> {
    logger.debug('[Billing] Billing disabled - no deduction');
    return { success: true, cost: 0, new_balance: 999999 };
  },

  async createCheckoutSession(_request: CreateCheckoutSessionRequest): Promise<CreateCheckoutSessionResponse> {
    logger.debug('[Billing] Billing disabled - checkout disabled');
    return { status: 'billing_disabled', message: 'Billing is disabled' };
  },

  async createPortalSession(_request: CreatePortalSessionRequest): Promise<CreatePortalSessionResponse> {
    logger.debug('[Billing] Billing disabled - portal disabled');
    return { portal_url: '#billing-disabled' };
  },

  async cancelSubscription(_request?: CancelSubscriptionRequest): Promise<CancelSubscriptionResponse> {
    logger.debug('[Billing] Billing disabled - cancel disabled');
    return { success: true, cancel_at: 0, message: 'Billing is disabled' };
  },

  async reactivateSubscription(): Promise<ReactivateSubscriptionResponse> {
    logger.debug('[Billing] Billing disabled - reactivate disabled');
    return { success: true, message: 'Billing is disabled' };
  },

  async purchaseCredits(_request: PurchaseCreditsRequest): Promise<PurchaseCreditsResponse> {
    logger.debug('[Billing] Billing disabled - purchase disabled');
    return { checkout_url: '#billing-disabled' };
  },

  async getTransactions(_limit = 50, _offset = 0): Promise<{ transactions: Transaction[]; count: number }> {
    logger.debug('[Billing] Billing disabled - no transactions');
    return { transactions: [], count: 0 };
  },

  async getUsageHistory(_days = 30): Promise<UsageHistory> {
    logger.debug('[Billing] Billing disabled - no usage history');
    return { daily_usage: {}, total_period_usage: 0, total_period_credits: 999999 };
  },

  async getTrialStatus(): Promise<TrialStatus> {
    logger.debug('[Billing] Billing disabled - no trial');
    return { has_trial: false, can_start_trial: false, message: 'Billing is disabled' };
  },

  async startTrial(_request: TrialStartRequest): Promise<TrialStartResponse> {
    logger.debug('[Billing] Billing disabled - trial disabled');
    return { checkout_url: '#billing-disabled', session_id: '' };
  },

  async createTrialCheckout(_request: TrialCheckoutRequest): Promise<TrialCheckoutResponse> {
    logger.debug('[Billing] Billing disabled - trial checkout disabled');
    return { checkout_url: '#billing-disabled', session_id: '' };
  },

  async cancelTrial(): Promise<{ success: boolean; message: string; subscription_status: string }> {
    logger.debug('[Billing] Billing disabled - cancel trial disabled');
    return { success: true, message: 'Billing is disabled', subscription_status: 'none' };
  },

  async scheduleDowngrade(_request: ScheduleDowngradeRequest): Promise<ScheduleDowngradeResponse> {
    logger.debug('[Billing] Billing disabled - downgrade disabled');
    return {
      success: true,
      message: 'Billing is disabled',
      scheduled_date: '',
      current_tier: { name: 'unlimited', display_name: 'Unlimited', monthly_credits: 999999 },
      target_tier: { name: 'unlimited', display_name: 'Unlimited', monthly_credits: 999999 },
      billing_change: false,
      current_billing_period: '',
      target_billing_period: '',
      change_description: 'Billing is disabled'
    };
  },

  async cancelScheduledChange(): Promise<CancelScheduledChangeResponse> {
    logger.debug('[Billing] Billing disabled - cancel scheduled change disabled');
    return { success: true, message: 'Billing is disabled' };
  },

  async syncSubscription(): Promise<{ success: boolean; message: string }> {
    logger.debug('[Billing] Billing disabled - sync disabled');
    return { success: true, message: 'Billing is disabled' };
  },

  async getCheckoutSession(_sessionId: string): Promise<CheckoutSessionDetails | null> {
    logger.debug('[Billing] Billing disabled - checkout session disabled');
    return null;
  }
};

// =============================================================================
// CONVENIENCE EXPORTS - All return mock/disabled data
// =============================================================================

export const getAccountState = (skipCache?: boolean) => billingApi.getAccountState(skipCache);
export const deductTokenUsage = (usage: TokenUsage) => billingApi.deductTokenUsage(usage);
export const createCheckoutSession = (request: CreateCheckoutSessionRequest) => billingApi.createCheckoutSession(request);
export const createPortalSession = (request: CreatePortalSessionRequest) => billingApi.createPortalSession(request);
export const cancelSubscription = (feedback?: string) => billingApi.cancelSubscription(feedback ? { feedback } : undefined);
export const reactivateSubscription = () => billingApi.reactivateSubscription();
export const purchaseCredits = (request: PurchaseCreditsRequest) => billingApi.purchaseCredits(request);
export const getTransactions = (limit?: number, offset?: number) => billingApi.getTransactions(limit, offset);
export const getUsageHistory = (days?: number) => billingApi.getUsageHistory(days);
export const getTrialStatus = () => billingApi.getTrialStatus();
export const startTrial = (request: TrialStartRequest) => billingApi.startTrial(request);
export const createTrialCheckout = (request: TrialCheckoutRequest) => billingApi.createTrialCheckout(request);
export const cancelTrial = () => billingApi.cancelTrial();
export const scheduleDowngrade = (request: ScheduleDowngradeRequest) => billingApi.scheduleDowngrade(request);
export const cancelScheduledChange = () => billingApi.cancelScheduledChange();
export const syncSubscription = () => billingApi.syncSubscription();
export const getCheckoutSession = (sessionId: string) => billingApi.getCheckoutSession(sessionId);

export async function createInlineCheckout(_request: CreateInlineCheckoutRequest): Promise<CreateInlineCheckoutResponse> {
  logger.debug('[Billing] Billing disabled - inline checkout disabled');
  return { subscription_id: '', tier_key: 'unlimited', message: 'Billing is disabled' };
}

export async function confirmInlineCheckout(_request: ConfirmInlineCheckoutRequest): Promise<ConfirmInlineCheckoutResponse> {
  logger.debug('[Billing] Billing disabled - confirm checkout disabled');
  return { success: true, tier: 'unlimited', message: 'Billing is disabled' };
}
