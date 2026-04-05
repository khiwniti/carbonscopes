'use client';
import { logger } from '@/lib/logger';

import { useEffect, useRef } from 'react';
import { useCarbonScopeComputerStore } from '@/stores/carbonscope-computer-store';

type Mode = 'slides' | 'sheets' | 'docs' | 'canvas' | 'video' | 'research';

/**
 * Hook to auto-open viewers based on mode selection from /thread/new
 * Reads mode from sessionStorage and opens the appropriate viewer
 */
export function useModeViewerInit(
  threadId: string,
  projectId: string,
  sandboxId?: string,
  accessToken?: string
) {
  const hasInitialized = useRef(false);
  const openFileBrowser = useCarbonScopeComputerStore((state) => state.openFileBrowser);

  useEffect(() => {
    // Only run once per thread
    if (hasInitialized.current) return;

    const threadMode = sessionStorage.getItem('thread_mode') as Mode | null;
    const shouldAutoOpen = sessionStorage.getItem('thread_mode_auto_open') === 'true';
    const currentThreadId = sessionStorage.getItem('optimistic_thread');

    // Only auto-open if this is the thread that was just created with a mode
    if (!threadMode || !shouldAutoOpen || currentThreadId !== threadId) {
      return;
    }

    hasInitialized.current = true;

    logger.log('[ModeViewerInit] Auto-opening viewer for mode:', threadMode);

    // Clean up sessionStorage
    sessionStorage.removeItem('thread_mode');
    sessionStorage.removeItem('thread_mode_auto_open');

    // Wait a bit for the thread to initialize
    const initTimeout = setTimeout(() => {
      handleModeInit(threadMode, openFileBrowser);
    }, 1000);

    return () => clearTimeout(initTimeout);
  }, [threadId, openFileBrowser]);
}

/**
 * Handles mode-specific initialization
 */
function handleModeInit(mode: Mode, openFileBrowser: () => void) {
  switch (mode) {
    case 'slides':
      // Open Files tab in CarbonScope Computer to show presentations folder
      openFileBrowser();
      logger.log('[ModeViewerInit] Opening Files panel for presentations');
      break;

    case 'sheets':
      // Open Files tab to show spreadsheets
      openFileBrowser();
      logger.log('[ModeViewerInit] Opening Files panel for spreadsheets');
      break;

    case 'docs':
      // Open Files tab to show documents
      openFileBrowser();
      logger.log('[ModeViewerInit] Opening Files panel for documents');
      break;

    case 'canvas':
      // Open Files tab for canvas files
      openFileBrowser();
      logger.log('[ModeViewerInit] Opening Files panel for canvas');
      break;

    case 'video':
      // Open Files tab for video files
      openFileBrowser();
      logger.log('[ModeViewerInit] Opening Files panel for video');
      break;

    case 'research':
      // For research mode, just keep the default view
      // The agent will show research results in the chat
      logger.log('[ModeViewerInit] Research mode - keeping default view');
      break;

    default:
      logger.warn('[ModeViewerInit] Unknown mode:', mode);
  }
}

