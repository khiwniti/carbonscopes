/**
 * TODO: BILLING DISABLED - This component is dead code. It returns null
 * unconditionally. All consumers that open this modal (chat-input.tsx,
 * nav-user-with-teams.tsx, credits-display.tsx, ThreadComponent.tsx)
 * call setPlanSelectionModalOpen(true) which opens an empty dialog.
 * Remove or re-enable when billing is turned back on.
 */
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
