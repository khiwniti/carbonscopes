import * as React from 'react';
import { type ViewProps } from 'react-native';
import { Avatar } from '@/components/ui/Avatar';
import type { Agent } from '@/api/types';

interface AgentAvatarProps extends ViewProps {
  agent?: Agent;
  size?: number;
}

/**
 * AgentAvatar Component - Agent-specific wrapper around unified Avatar
 * 
 * Uses the unified Avatar component with agent-specific configuration.
 * Automatically handles:
 * - Agent icon from backend (icon_name)
 * - Agent colors (icon_color, icon_background)
 * - carbonscope/CarbonScope SUPER WORKER special case (CarbonScope symbol)
 * - Fallback to agent name initial
 * 
 * @example
 * <AgentAvatar agent={agent} size={48} />
 */
export function AgentAvatar({ agent, size = 48, style, ...props }: AgentAvatarProps) {
  // Check if this is the carbonscope/CarbonScope SUPER WORKER
  const iscarbonscopeAgent = agent?.metadata?.is_carbonscope_default || 
                      agent?.name?.toLowerCase() === 'carbonscope' ||
                      agent?.name?.toLowerCase() === 'superworker' ||
                      agent?.name?.toLowerCase() === 'CarbonScope super worker';

  return (
    <Avatar
      variant="agent"
      size={size}
      icon={agent?.icon_name || undefined}
      iconColor={iscarbonscopeAgent ? undefined : agent?.icon_color}
      backgroundColor={iscarbonscopeAgent ? undefined : agent?.icon_background}
      useCarbonScopeSymbol={iscarbonscopeAgent}
      fallbackText={agent?.name}
      style={style}
      {...props}
    />
  );
}

