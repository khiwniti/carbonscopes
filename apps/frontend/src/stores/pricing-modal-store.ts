/**
 * BILLING DISABLED - Pricing modal will never open
 */
import { create } from 'zustand';

interface PricingModalState {
  isOpen: boolean;
  customTitle?: string;
  isAlert?: boolean;
  alertTitle?: string;
  alertSubtitle?: string;
  returnUrl?: string;
  openPricingModal: (options?: { title?: string; returnUrl?: string, isAlert?: boolean, alertTitle?: string, alertSubtitle?: string }) => void;
  closePricingModal: () => void;
}

export const usePricingModalStore = create<PricingModalState>((set) => ({
  isOpen: false,
  isAlert: false,
  customTitle: undefined,
  alertSubtitle: undefined,
  returnUrl: undefined,
  // BILLING DISABLED - Never open pricing modal
  openPricingModal: (_options) => {
    console.debug('[Billing] Billing disabled - pricing modal will not open');
    // Do nothing - billing is disabled
  },
  closePricingModal: () =>
    set({
      isOpen: false,
      customTitle: undefined,
      isAlert: false,
      alertTitle: undefined,
      alertSubtitle: undefined,
      returnUrl: undefined,
    }),
}));
