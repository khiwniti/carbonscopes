import { Metadata } from 'next';
import { redirect } from 'next/navigation';

export const metadata: Metadata = {
  title: 'Worker Conversation | CarbonScope',
  description: 'Interactive Worker conversation powered by CarbonScope',
  openGraph: {
    title: 'Worker Conversation | CarbonScope',
    description: 'Interactive Worker conversation powered by CarbonScope',
    type: 'website',
  },
};

export default async function AgentsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
