'use client';

import { memo, useState, useRef, useEffect, useCallback, KeyboardEvent } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useTheme } from 'next-themes';
import { cn } from '@/lib/utils';
import { carbonScope } from '@/lib/design-tokens';
import { backendApi } from '@/lib/api-client';
import { CarbonScopeLoader } from '@/components/ui/carbonscope-loader';
import { fileQueryKeys } from '@/hooks/files/use-file-queries';

interface TerminalLine {
  id: string;
  type: 'input' | 'output' | 'error';
  content: string;
  cwd?: string;
}

interface TerminalProps {
  sandboxId: string;
  className?: string;
}

const TERMINAL_HISTORY_KEY = 'CarbonScope-terminal-history';

export const Terminal = memo(function Terminal({ sandboxId, className }: TerminalProps) {
  const queryClient = useQueryClient();
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';
  const c = carbonScope.colors;
  const [lines, setLines] = useState<TerminalLine[]>([
    { id: '0', type: 'output', content: 'Welcome to CarbonScope Terminal' },
    { id: '1', type: 'output', content: 'Type commands below and press Enter to execute.' },
    { id: '2', type: 'output', content: '' },
  ]);
  const [currentInput, setCurrentInput] = useState('');
  const [cwd, setCwd] = useState('/workspace');
  const [isExecuting, setIsExecuting] = useState(false);
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [isUserScrolling, setIsUserScrolling] = useState(false);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const lineIdRef = useRef(3);

  const invalidateFileQueries = useCallback(() => {
    queryClient.invalidateQueries({
      queryKey: fileQueryKeys.directories(),
    });
  }, [queryClient]);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(TERMINAL_HISTORY_KEY);
      if (saved) {
        setCommandHistory(JSON.parse(saved));
      }
    } catch (e) {
    }
  }, []);

  const isNearBottom = useCallback(() => {
    if (!containerRef.current) return true;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    return scrollHeight - scrollTop - clientHeight < 50;
  }, []);

  const scrollToBottom = useCallback(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, []);

  const handleScroll = useCallback(() => {
    if (isNearBottom()) {
      setIsUserScrolling(false);
    } else {
      setIsUserScrolling(true);
    }
  }, [isNearBottom]);

  useEffect(() => {
    if (!isUserScrolling) {
      scrollToBottom();
    }
  }, [lines, scrollToBottom, isUserScrolling]);

  const focusInput = useCallback(() => {
    inputRef.current?.focus();
  }, []);

  const addLine = useCallback((type: TerminalLine['type'], content: string, lineCwd?: string) => {
    const id = String(lineIdRef.current++);
    setLines(prev => [...prev, { id, type, content, cwd: lineCwd }]);
  }, []);

  const executeCommand = useCallback(async (command: string) => {
    if (!command.trim() || !sandboxId) return;

    addLine('input', command, cwd);

    if (command.trim().startsWith('cd ')) {
      const newPath = command.trim().slice(3).trim();
      let targetPath: string;
      
      if (newPath.startsWith('/')) {
        targetPath = newPath;
      } else if (newPath === '..') {
        const parts = cwd.split('/').filter(Boolean);
        parts.pop();
        targetPath = '/' + parts.join('/') || '/';
      } else if (newPath === '~') {
        targetPath = '/workspace';
      } else {
        targetPath = cwd.endsWith('/') ? cwd + newPath : cwd + '/' + newPath;
      }
      
      setCwd(targetPath);
      addLine('output', '');
      setCurrentInput('');
      
      setCommandHistory(prev => {
        const updated = [...prev.filter(c => c !== command), command].slice(-100);
        localStorage.setItem(TERMINAL_HISTORY_KEY, JSON.stringify(updated));
        return updated;
      });
      setHistoryIndex(-1);
      return;
    }

    if (command.trim() === 'clear') {
      setLines([]);
      setCurrentInput('');
      return;
    }

    setIsExecuting(true);
    setCurrentInput('');

    setCommandHistory(prev => {
      const updated = [...prev.filter(c => c !== command), command].slice(-100);
      localStorage.setItem(TERMINAL_HISTORY_KEY, JSON.stringify(updated));
      return updated;
    });
    setHistoryIndex(-1);

    try {
      const response = await backendApi.post<{ output: string; exit_code: number; success: boolean }>(
        `/sandboxes/${sandboxId}/terminal/execute`,
        { command, cwd },
        { showErrors: false }
      );

      if (!response.success || response.error) {
        addLine('error', `Error: ${response.error?.message || 'Command execution failed'}`);
        setIsExecuting(false);
        return;
      }

      const result = response.data;
      
      if (result?.output) {
        const outputLines = result.output.split('\n');
        outputLines.forEach((line: string) => {
          addLine(result.success ? 'output' : 'error', line);
        });
      } else if (!result?.success) {
        addLine('error', 'Command failed with no output');
      } else {
        addLine('output', '');
      }

    } catch (error) {
      addLine('error', `Failed to execute command: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsExecuting(false);
      invalidateFileQueries();
    }
  }, [sandboxId, cwd, addLine, invalidateFileQueries]);

  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isExecuting) {
      executeCommand(currentInput);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        const newIndex = historyIndex < commandHistory.length - 1 ? historyIndex + 1 : historyIndex;
        setHistoryIndex(newIndex);
        setCurrentInput(commandHistory[commandHistory.length - 1 - newIndex] || '');
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setCurrentInput(commandHistory[commandHistory.length - 1 - newIndex] || '');
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setCurrentInput('');
      }
    } else if (e.key === 'c' && e.ctrlKey) {
      if (isExecuting) {
        addLine('output', '^C');
      }
      setCurrentInput('');
    } else if (e.key === 'l' && e.ctrlKey) {
      e.preventDefault();
      setLines([]);
    }
  }, [currentInput, isExecuting, executeCommand, commandHistory, historyIndex, addLine]);

  const getPromptDisplay = (path: string) => {
    const shortPath = path.replace('/workspace', '~');
    return shortPath || '/';
  };

  return (
    <div 
      className={cn(
        "flex flex-col h-full text-sm overflow-hidden",
        "[font-family:var(--cs-font-mono,ui-monospace),ui-monospace]",
        !isDark && "bg-zinc-100 text-zinc-800",
        className
      )}
      style={
        isDark
          ? { backgroundColor: c.backgroundAlt, color: c.textSecondary }
          : undefined
      }
      onClick={focusInput}
    >
      <div
        className={cn(
          "flex items-center h-7 px-3 gap-2 flex-shrink-0 border-b",
          !isDark && "bg-zinc-200/80 border-zinc-300"
        )}
        style={
          isDark
            ? {
                backgroundColor: c.backgroundSubtle,
                borderColor: c.border,
              }
            : undefined
        }
      >
        <span
          className={cn("text-xs", !isDark && "text-zinc-500")}
          style={isDark ? { color: c.textMuted } : undefined}
        >
          {getPromptDisplay(cwd)} — bash
        </span>
        {isExecuting && (
          <CarbonScopeLoader size="small" className="ml-auto" />
        )}
      </div>

      <div 
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-auto p-3 space-y-0.5"
      >
        {lines.map((line) => (
          <div key={line.id} className="flex items-start">
            {line.type === 'input' ? (
              <>
                <span
                  className={cn("mr-1.5", !isDark && "text-blue-500")}
                  style={isDark ? { color: c.lifecycle.a4a5Light } : undefined}
                >
                  {getPromptDisplay(line.cwd || '/workspace')}
                </span>
                <span
                  className={cn("mr-2", !isDark && "text-emerald-600")}
                  style={isDark ? { color: c.primaryLight } : undefined}
                >
                  ❯
                </span>
                <span
                  className={cn(!isDark && "text-zinc-900")}
                  style={isDark ? { color: c.textPrimary } : undefined}
                >
                  {line.content}
                </span>
              </>
            ) : (
              <span
                className={cn(
                  "whitespace-pre-wrap break-all",
                  !isDark && line.type === 'error' && "text-red-600",
                  !isDark && line.type !== 'error' && "text-zinc-700"
                )}
                style={
                  isDark
                    ? {
                        color: line.type === 'error' ? c.lifecycle.c1c4Light : c.textSecondary,
                      }
                    : undefined
                }
              >
                {line.content}
              </span>
            )}
          </div>
        ))}

        <div className="flex items-center">
          <span
            className={cn("mr-1.5", !isDark && "text-blue-500")}
            style={isDark ? { color: c.lifecycle.a4a5Light } : undefined}
          >
            {getPromptDisplay(cwd)}
          </span>
          <span
            className={cn("mr-2", !isDark && "text-emerald-600")}
            style={isDark ? { color: c.primaryLight } : undefined}
          >
            ❯
          </span>
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isExecuting}
              autoFocus
              spellCheck={false}
              autoComplete="off"
              autoCapitalize="off"
              className={cn(
                "w-full bg-transparent outline-none",
                !isDark && "text-zinc-900 caret-blue-500 placeholder:text-zinc-400",
                isDark && "placeholder:text-slate-500",
                isExecuting && "opacity-50"
              )}
              style={
                isDark
                  ? {
                      color: c.textPrimary,
                      caretColor: c.lifecycle.a4a5Light,
                    }
                  : undefined
              }
              placeholder={isExecuting ? "Executing..." : ""}
            />
          </div>
        </div>
      </div>
    </div>
  );
});

Terminal.displayName = 'Terminal';
