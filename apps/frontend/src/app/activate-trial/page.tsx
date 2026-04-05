/**
 * BILLING DISABLED - Redirect to dashboard
 */
import { redirect } from 'next/navigation';

export default function ActivateTrialPage() {
  redirect('/dashboard');
}
