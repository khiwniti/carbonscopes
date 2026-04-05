'use client';

import dynamic from 'next/dynamic';
import React from 'react';
import { CarbonScopeLoader } from '@/components/ui/carbonscope-loader';
import { cn } from '@/lib/utils';

const MermaidRendererClient = dynamic(
  () => import('./mermaid-renderer-client').then(mod => ({ default: mod.MermaidRendererClient })),
  {
    ssr: false,
    loading: () => (
      <div className={cn('flex items-center justify-center p-8 bg-muted/30 rounded-2xl border border-dashed')}>
        <div className="text-center">
          <div className="text-sm text-muted-foreground mb-2">🎨 Loading diagram renderer...</div>
          <CarbonScopeLoader size="medium" />
        </div>
      </div>
    )
  }
);

interface MermaidRendererProps {
  chart: string;
  className?: string;
  enableFullscreen?: boolean;
}

export const MermaidRenderer: React.FC<MermaidRendererProps> = (props) => {
  return <MermaidRendererClient {...props} />;
};

MermaidRenderer.displayName = 'MermaidRenderer';
