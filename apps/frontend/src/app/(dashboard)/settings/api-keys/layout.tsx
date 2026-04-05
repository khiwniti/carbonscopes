import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'API Keys | CarbonScope',
  description: 'Manage your API keys for programmatic access to CarbonScope',
  openGraph: {
    title: 'API Keys | CarbonScope',
    description: 'Manage your API keys for programmatic access to CarbonScope',
    type: 'website',
  },
};

export default async function APIKeysLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
