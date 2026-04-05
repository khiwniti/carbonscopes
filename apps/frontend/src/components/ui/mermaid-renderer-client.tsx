'use client';
import { logger } from '@/lib/logger';
import { getSafeHtml } from '@/lib/sanitize';

import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { cn } from '@/lib/utils';
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Maximize2, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { CarbonScopeLoader } from '@/components/ui/carbonscope-loader';

// Global cache for rendered Mermaid diagrams
const mermaidCache = new Map<string, string>();
let mermaidInstance: any = null;

// Global cleanup function to remove any Mermaid error messages from the DOM
const cleanupMermaidErrors = () => {
  const allElements = document.querySelectorAll('div, span, p, text, tspan');
  let cleaned = 0;
  allElements.forEach(el => {
    const textContent = el.textContent || '';
    if (textContent.includes('Syntax error in text') || 
        textContent.includes('mermaid version 11.12.0') ||
        textContent.trim() === 'Syntax error in text') {
      el.remove();
      cleaned++;
    }
  });
  
  if (cleaned > 0) {
    logger.log(`🧹 Cleaned up ${cleaned} Mermaid error elements`);
  }
};

interface MermaidRendererClientProps {
  chart: string;
  className?: string;
  enableFullscreen?: boolean;
}

export const MermaidRendererClient: React.FC<MermaidRendererClientProps> = React.memo(({
  chart,
  className,
  enableFullscreen = true
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [renderedContent, setRenderedContent] = useState<string>('');
  const [isFullscreenOpen, setIsFullscreenOpen] = useState(false);
  const [fullscreenRenderedContent, setFullscreenRenderedContent] = useState<string>('');

  // Create a stable hash for the chart content to enable caching
  const chartHash = useMemo(() => {
    let hash = 0;
    const trimmed = chart.trim();
    for (let i = 0; i < trimmed.length; i++) {
      const char = trimmed.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash.toString(36);
  }, [chart]);

  // Canvas state
  const canvasRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Cleanup periodic check
  useEffect(() => {
    const cleanupInterval = setInterval(cleanupMermaidErrors, 5000);
    cleanupMermaidErrors();
    return () => clearInterval(cleanupInterval);
  }, []);

  // Canvas handlers
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 0) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
    }
  }, [panOffset]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isDragging) {
      setPanOffset({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  }, [isDragging, dragStart]);

  const handleMouseUp = useCallback(() => setIsDragging(false), []);

  const handleZoomIn = () => setZoom(prev => Math.min(5, prev * 1.2));
  const handleZoomOut = () => setZoom(prev => Math.max(0.1, prev * 0.8));
  const handleResetView = () => {
    setZoom(1);
    setPanOffset({ x: 0, y: 0 });
  };
  const handleFitToViewport = () => {
    setZoom(0.8);
    setPanOffset({ x: 0, y: 0 });
  };

  const handleFullscreenOpen = () => {
    if (enableFullscreen) {
      setIsFullscreenOpen(true);
      setZoom(0.8);
      setPanOffset({ x: 0, y: 0 });
      setIsDragging(false);
      renderChartForFullscreen();
    }
  };

  const renderChartForFullscreen = async () => {
    try {
      const cachedResult = mermaidCache.get(chartHash);
      if (cachedResult) {
        setFullscreenRenderedContent(cachedResult);
        return;
      }

      if (!mermaidInstance) {
        const mermaid = (await import('mermaid')).default;
        await mermaid.initialize({
          startOnLoad: false,
          securityLevel: 'strict',
          theme: 'base',
          fontFamily: 'ui-sans-serif, system-ui, sans-serif',
          gitGraph: {
            showBranches: true,
            showCommitLabel: true,
            mainBranchName: 'main',
            rotateCommitLabel: true
          }
        });
        mermaidInstance = mermaid;
      }

      const chartId = `mermaid-fullscreen-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const result = await mermaidInstance.render(chartId, chart);
      mermaidCache.set(chartHash, result.svg);
      setFullscreenRenderedContent(result.svg);
    } catch (err) {
      console.error('Fullscreen rendering error:', err);
      if (isFullscreenOpen) {
        setFullscreenRenderedContent(`
          <div style="display: flex; align-items: center; justify-content: center; height: 200px; color: #6b7280;">
            <div style="text-align: center;">
              <div style="font-size: 24px; margin-bottom: 8px;">📊</div>
              <div>Diagram rendering failed</div>
            </div>
          </div>
        `);
      }
    }
  };

  useEffect(() => {
    let mounted = true;

    const renderChart = async () => {
      if (!chart.trim()) {
        if (mounted) setIsLoading(false);
        return;
      }

      const cachedResult = mermaidCache.get(chartHash);
      if (cachedResult) {
        if (mounted) {
          setRenderedContent(cachedResult);
          setIsLoading(false);
        }
        return;
      }

      try {
        if (mounted) {
          setIsLoading(true);
          setError(null);
        }

        const trimmedChart = chart.trim();
        if (!trimmedChart) {
          throw new Error('Empty chart content');
        }

        const firstLine = trimmedChart.split('\n')[0].toLowerCase().trim();
        const validStarters = [
          'graph', 'flowchart', 'sequencediagram', 'sequence', 'classdiagram', 'class',
          'statediagram', 'state', 'erdiagram', 'journey', 'gantt', 'pie',
          'gitgraph', 'mindmap', 'timeline', 'sankey', 'block',
          'quadrant', 'requirement', 'c4context', 'c4container',
          'c4component', 'c4dynamic'
        ];
        
        const hasValidStarter = validStarters.some(starter => 
          firstLine.startsWith(starter) || firstLine.includes(starter)
        );

        if (!hasValidStarter) {
          throw new Error(`Invalid diagram type. Chart must start with a valid Mermaid diagram type. Found: "${firstLine}"`);
        }

        if (!mermaidInstance) {
          const mermaid = (await import('mermaid')).default;
          await mermaid.initialize({
            startOnLoad: false,
            securityLevel: 'strict',
            theme: 'base',
            fontFamily: 'ui-sans-serif, system-ui, sans-serif',
            gitGraph: {
              showBranches: true,
              showCommitLabel: true,
              mainBranchName: 'main',
              rotateCommitLabel: true
            }
          });
          mermaidInstance = mermaid;
        }

        const chartId = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        let result;
        try {
          result = await mermaidInstance.render(chartId, trimmedChart);
        } catch (renderError) {
          const errorMessage = renderError instanceof Error ? renderError.message : String(renderError);
          const errorElement = document.getElementById(chartId);
          if (errorElement) errorElement.remove();
          
          if (errorMessage.includes('Parse error') || errorMessage.includes('Syntax error')) {
            throw new Error(`Diagram syntax error: ${errorMessage}`);
          } else if (errorMessage.includes('UnknownDiagramError')) {
            throw new Error('unsupported_diagram_type');
          } else {
            throw new Error(`Failed to render diagram: ${errorMessage}`);
          }
        }

        if (!mounted) return;

        mermaidCache.set(chartHash, result.svg);
        setRenderedContent(result.svg);
        setTimeout(cleanupMermaidErrors, 100);

      } catch (err) {
        console.error('Mermaid rendering error:', err);
        setTimeout(cleanupMermaidErrors, 50);
        
        if (mounted) {
          const errorMessage = err instanceof Error ? err.message : 'Failed to render diagram';
          
          if (errorMessage.includes('UnknownDiagramError') || errorMessage.includes('No diagram type detected')) {
            setError('unsupported_diagram_type');
          } else {
            setError(errorMessage);
          }
        }
      } finally {
        if (mounted) setIsLoading(false);
      }
    };

    renderChart();

    return () => {
      mounted = false;
    };
  }, [chartHash, chart]);

  if (isLoading) {
    return (
      <div className={cn('flex items-center justify-center p-8 bg-muted/30 rounded-2xl border border-dashed', className)}>
        <div className="text-center">
          <div className="text-sm text-muted-foreground mb-2">🎨 Rendering Mermaid diagram...</div>
          <CarbonScopeLoader size="medium" />
        </div>
      </div>
    );
  }

  if (error) {
    if (error === 'unsupported_diagram_type') {
      return (
        <div className={cn('my-2', className)}>
          <div className="text-xs text-muted-foreground mb-1 flex items-center gap-1">
            <span>⚠️</span>
            <span>Unsupported diagram type</span>
          </div>
          <pre className="text-xs p-3 bg-muted/50 border rounded-2xl overflow-x-auto whitespace-pre-wrap font-mono">
            {chart}
          </pre>
        </div>
      );
    }

    return (
      <div className={cn('p-4 bg-destructive/10 border border-destructive/20 rounded-2xl', className)}>
        <div className="text-sm text-destructive font-medium mb-2">
          ❌ Failed to render Mermaid diagram
        </div>
        <div className="text-xs text-muted-foreground font-mono bg-muted/50 p-2 rounded">
          {error}
        </div>
        <details className="mt-2">
          <summary className="text-xs text-muted-foreground cursor-pointer hover:text-foreground">
            📄 Show diagram source
          </summary>
          <pre className="text-xs mt-2 p-2 bg-muted/50 rounded overflow-x-auto whitespace-pre-wrap">
            {chart}
          </pre>
        </details>
      </div>
    );
  }

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: `
        .mermaid-container svg {
          max-width: 100% !important;
          height: auto !important;
          display: block !important;
          margin: 0 auto !important;
        }
        .mermaid-container .node {
          fill: hsl(var(--card)) !important;
          stroke: hsl(var(--foreground)) !important;
        }
        .mermaid-container text {
          fill: hsl(var(--foreground)) !important;
          font-family: var(--font-geist-sans), ui-sans-serif, system-ui, sans-serif !important;
        }
      ` }} />
      <div
        className={cn(
          'mermaid-container my-4 rounded-2xl border overflow-auto bg-background relative group cursor-pointer',
          enableFullscreen && 'hover:ring-2 hover:ring-primary/20',
          className
        )}
        style={{ minHeight: '200px', width: '100%' }}
        onClick={enableFullscreen ? handleFullscreenOpen : undefined}
      >
        <div ref={containerRef} dangerouslySetInnerHTML={getSafeHtml(renderedContent)} />
        {enableFullscreen && (
          <div className="absolute inset-0 bg-black/0 hover:bg-black/5 transition-colors rounded-2xl flex items-center justify-center opacity-0 hover:opacity-100 pointer-events-none">
            <Button
              variant="secondary"
              size="sm"
              className="h-8 w-8 p-0 bg-background/90 hover:bg-background border shadow-sm pointer-events-auto"
              onClick={(e) => {
                e.stopPropagation();
                handleFullscreenOpen();
              }}
              title="View fullscreen"
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>

      <Dialog open={isFullscreenOpen} onOpenChange={setIsFullscreenOpen}>
        <DialogContent className="max-w-[95vw] max-h-[95vh] w-full h-full p-0 overflow-hidden">
          <div className="flex flex-col h-full bg-background">
            <div className="flex items-center justify-between p-4 pr-16 border-b bg-background/95 backdrop-blur-sm">
              <div className="flex items-center gap-2">
                <DialogTitle className="text-sm font-medium">Mermaid Diagram</DialogTitle>
                <span className="text-xs text-muted-foreground">
                  Zoom: {Math.round(zoom * 100)}%
                </span>
              </div>

              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={handleZoomOut} className="h-8 w-8 p-0" title="Zoom out">
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm" onClick={handleResetView} className="h-8 w-8 p-0" title="Reset view">
                  <RotateCcw className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm" onClick={handleZoomIn} className="h-8 w-8 p-0" title="Zoom in">
                  <ZoomIn className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm" onClick={handleFitToViewport} className="h-8 px-3" title="Fit to viewport">
                  Fit
                </Button>
              </div>
            </div>

            <div
              ref={canvasRef}
              className="flex-1 min-h-0 relative overflow-hidden bg-muted/10 cursor-move touch-none select-none"
              onClick={(e) => e.stopPropagation()}
              onMouseDown={(e) => {
                e.stopPropagation();
                handleMouseDown(e);
              }}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
            >
              {fullscreenRenderedContent ? (
                <div
                  className="absolute inset-0 flex items-center justify-center"
                  style={{
                    transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoom})`,
                    transformOrigin: 'center center',
                    transition: isDragging ? 'none' : 'transform 0.1s ease-out'
                  }}
                  dangerouslySetInnerHTML={getSafeHtml(fullscreenRenderedContent)}
                />
              ) : (
                <div className="flex items-center justify-center h-full w-full">
                  <div className="text-center">
                    <div className="text-sm text-muted-foreground mb-2">🎨 Loading fullscreen diagram...</div>
                    <CarbonScopeLoader size="medium" />
                  </div>
                </div>
              )}

              <div className="absolute bottom-4 left-4 bg-background/80 backdrop-blur-sm rounded-2xl px-3 py-2 text-xs text-muted-foreground shadow-sm">
                <div>Drag to pan • Scroll to zoom</div>
                <div className="mt-1 opacity-75">Esc: close • +/-: zoom • 0: reset • F: fit</div>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
});

MermaidRendererClient.displayName = 'MermaidRendererClient';
