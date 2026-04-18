'use client';
import { BACKEND_URL } from '@/lib/api-client';
import { logger } from '@/lib/logger';

import { memo, useRef, useEffect, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useTheme } from 'next-themes';
import { cn } from '@/lib/utils';
import { Terminal as XTerm, ITheme } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import '@xterm/xterm/css/xterm.css';
import { useAuth } from '@/components/AuthProvider';
import { fileQueryKeys } from '@/hooks/files/use-file-queries';
import { carbonScope } from '@/lib/design-tokens';

interface SSHTerminalProps {
  sandboxId: string;
  className?: string;
}

function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

const xtermMono = `${carbonScope.typography.fontMono}, Menlo, Monaco, Consolas, monospace`;

const darkTheme: ITheme = (() => {
  const c = carbonScope.colors;
  return {
    background: hexToRgba(c.background, 0.92),
    foreground: c.textSecondary,
    cursor: c.lifecycle.b1b5Light,
    cursorAccent: c.background,
    selectionBackground: 'rgba(16, 185, 129, 0.28)',
    black: c.surface,
    red: c.lifecycle.c1c4Light,
    green: c.primaryLight,
    yellow: c.warning,
    blue: c.lifecycle.a4a5Light,
    magenta: c.lifecycle.b1b5Light,
    cyan: c.info,
    white: c.textSecondary,
    brightBlack: c.textMuted,
    brightRed: c.lifecycle.c1c4Light,
    brightGreen: c.primaryLight,
    brightYellow: c.warning,
    brightBlue: c.lifecycle.a4a5Light,
    brightMagenta: c.lifecycle.b1b5Light,
    brightCyan: c.infoLight,
    brightWhite: c.textPrimary,
  };
})();

const lightTheme: ITheme = (() => {
  const c = carbonScope.colors;
  return {
    background: 'rgba(249, 250, 251, 0.94)',
    foreground: c.surfaceElevated,
    cursor: c.lifecycle.b1b5Dark,
    cursorAccent: c.textOnPrimary,
    selectionBackground: hexToRgba(c.primary, 0.12),
    black: c.surfaceElevated,
    red: c.errorDark,
    green: c.primaryDark,
    yellow: c.warningDark,
    blue: c.lifecycle.a4a5Dark,
    magenta: c.lifecycle.b1b5Dark,
    cyan: c.infoDark,
    white: c.textMuted,
    brightBlack: c.textDisabled,
    brightRed: c.error,
    brightGreen: c.primary,
    brightYellow: c.warning,
    brightBlue: c.info,
    brightMagenta: c.lifecycle.b1b5,
    brightCyan: c.info,
    brightWhite: c.textPrimary,
  };
})();

const getWebSocketUrl = () => {
  const baseUrl = BACKEND_URL || 'http://localhost:8000';
  return baseUrl.replace('https://', 'wss://').replace('http://', 'ws://');
};

let globalConnectionId = 0;

export const SSHTerminal = memo(function SSHTerminal({ sandboxId, className }: SSHTerminalProps) {
  const { session } = useAuth();
  const queryClient = useQueryClient();
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<XTerm | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const connectionIdRef = useRef<number>(0);
  const invalidateTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const invalidateFileQueries = useCallback(() => {
    if (invalidateTimeoutRef.current) {
      clearTimeout(invalidateTimeoutRef.current);
    }
    invalidateTimeoutRef.current = setTimeout(() => {
      queryClient.invalidateQueries({
        queryKey: fileQueryKeys.directories(),
      });
    }, 500);
  }, [queryClient]);

  const disconnect = useCallback(() => {
    connectionIdRef.current = 0;
    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onerror = null;
      wsRef.current.onclose = null;
      if (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING) {
        wsRef.current.close();
      }
      wsRef.current = null;
    }
  }, []);

  const connectWebSocket = useCallback((accessToken: string, term: XTerm) => {
    if (wsRef.current) {
      logger.log('[SSHTerminal] Already have a WebSocket, skipping');
      return;
    }

    globalConnectionId++;
    const myConnectionId = globalConnectionId;
    connectionIdRef.current = myConnectionId;

    const wsUrl = getWebSocketUrl();
    logger.log('[Terminal] Creating WebSocket (id:', myConnectionId, '):', `${wsUrl}/sandboxes/${sandboxId}/terminal/ws`);
    
    const ws = new WebSocket(`${wsUrl}/sandboxes/${sandboxId}/terminal/ws`);
    wsRef.current = ws;

    ws.onopen = () => {
      if (connectionIdRef.current !== myConnectionId) {
        logger.log('[SSHTerminal] Stale connection, closing');
        ws.close();
        return;
      }
      logger.log('[SSHTerminal] WebSocket open, sending auth...');
      try {
        ws.send(JSON.stringify({ type: 'auth', access_token: accessToken }));
        logger.log('[SSHTerminal] Auth sent');
      } catch (e) {
        console.error('[SSHTerminal] Failed to send auth:', e);
      }
    };

    ws.onmessage = (event) => {
      if (connectionIdRef.current !== myConnectionId) return;
      
      try {
        const message = JSON.parse(event.data);
        logger.log('[SSHTerminal] Message:', message.type, message.message || '');
        
        switch (message.type) {
          case 'status':
            term.writeln(`\x1b[33m${message.message}\x1b[0m`);
            break;
          case 'connected':
            term.writeln(`\x1b[32m${message.message}\x1b[0m`);
            term.writeln('');
            break;
          case 'output':
            if (message.data) {
              term.write(message.data);
            }
            break;
          case 'error':
            term.writeln(`\x1b[31mError: ${message.message}\x1b[0m`);
            break;
          case 'exit':
            term.writeln(`\x1b[33mSession ended with code: ${message.code}\x1b[0m`);
            wsRef.current = null;
            break;
        }
      } catch (e) {
        console.error('[SSHTerminal] Parse error:', e);
      }
    };

    ws.onerror = (error) => {
      if (connectionIdRef.current !== myConnectionId) return;
      console.error('[SSHTerminal] WebSocket error:', error);
    };

    ws.onclose = (event) => {
      if (connectionIdRef.current !== myConnectionId) return;
      logger.log('[SSHTerminal] WebSocket closed:', event.code);
      wsRef.current = null;
      term.writeln('\x1b[33mConnection closed\x1b[0m');
    };
  }, [sandboxId]);

  useEffect(() => {
    if (!terminalRef.current) return;

    const term = new XTerm({
      cursorBlink: true,
      cursorStyle: 'bar',
      fontSize: 13,
      fontFamily: xtermMono,
      theme: isDark ? darkTheme : lightTheme,
      allowProposedApi: true,
    });

    const fitAddon = new FitAddon();
    const webLinksAddon = new WebLinksAddon();
    
    term.loadAddon(fitAddon);
    term.loadAddon(webLinksAddon);
    
    term.open(terminalRef.current);
    fitAddon.fit();
    
    xtermRef.current = term;
    fitAddonRef.current = fitAddon;

    term.writeln('\x1b[38;5;141m┌──────────────────────────────────────────┐\x1b[0m');
    term.writeln('\x1b[38;5;141m│\x1b[0m   \x1b[1;38;5;183m◉\x1b[0m \x1b[1;37mCarbonScope\x1b[0m \x1b[38;5;245m• Terminal\x1b[0m               \x1b[38;5;141m│\x1b[0m');
    term.writeln('\x1b[38;5;141m└──────────────────────────────────────────┘\x1b[0m');
    term.writeln('');

    term.onData((data) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'input', data }));
        if (data.includes('\r') || data.includes('\n')) {
          invalidateFileQueries();
        }
      }
    });

    term.onResize(({ cols, rows }) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'resize', cols, rows }));
      }
    });

    const handleResize = () => fitAddonRef.current?.fit();
    window.addEventListener('resize', handleResize);
    
    const container = terminalRef.current;
    const resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(container);

    return () => {
      window.removeEventListener('resize', handleResize);
      resizeObserver.disconnect();
      if (invalidateTimeoutRef.current) {
        clearTimeout(invalidateTimeoutRef.current);
      }
      disconnect();
      term.dispose();
      xtermRef.current = null;
      fitAddonRef.current = null;
    };
    // isDark is applied in the effect below so toggling theme does not dispose/reopen xterm.
    // eslint-disable-next-line react-hooks/exhaustive-deps -- see above
  }, [disconnect, invalidateFileQueries]);

  useEffect(() => {
    if (fitAddonRef.current) {
      setTimeout(() => fitAddonRef.current?.fit(), 100);
    }
  }, []);

  useEffect(() => {
    if (xtermRef.current) {
      xtermRef.current.options.theme = isDark ? darkTheme : lightTheme;
    }
  }, [isDark]);

  useEffect(() => {
    if (!session?.access_token || !sandboxId || !xtermRef.current || wsRef.current) {
      return;
    }
    
    logger.log('[SSHTerminal] Initiating connection...');
    connectWebSocket(session.access_token, xtermRef.current);
  }, [session?.access_token, sandboxId, connectWebSocket]);

  const shellBg = isDark
    ? `linear-gradient(180deg, ${carbonScope.colors.backgroundAlt} 0%, ${carbonScope.colors.background} 100%)`
    : 'linear-gradient(180deg, rgb(250 250 250) 0%, rgb(255 255 255) 100%)';

  return (
    <div
      className={cn(
        "flex flex-col h-full overflow-hidden",
        "bg-white/50 dark:bg-zinc-950/40",
        className
      )}
    >
      <div
        ref={terminalRef}
        className="flex-1 overflow-hidden"
        style={{
          padding: carbonScope.spacing[4],
          background: shellBg,
        }}
      />
    </div>
  );
});

SSHTerminal.displayName = 'SSHTerminal';
