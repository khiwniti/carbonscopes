/**
 * BILLING DISABLED - Plan selection modal never shows
 */
'use client';

interface PlanSelectionModalProps {
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
    returnUrl?: string;
    creditsExhausted?: boolean;
    upgradeReason?: string;
}

export function PlanSelectionModal(_props: PlanSelectionModalProps) {
    // Billing is disabled - modal never shows
    return null;
}
