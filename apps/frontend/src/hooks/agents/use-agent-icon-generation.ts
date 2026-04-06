import { useMutation } from '@tanstack/react-query';
import { logger } from '@/lib/logger';
import { generateAgentIcon, AgentIconGenerationRequest, AgentIconGenerationResponse } from '@/lib/api/agents';
import { toast } from '@/lib/toast';

export const useGenerateAgentIcon = () => {
  return useMutation<AgentIconGenerationResponse, Error, AgentIconGenerationRequest>({
    mutationFn: generateAgentIcon,
    onError: (error) => {
      logger.error('Error generating agent icon:', error);
      toast.error('Failed to generate Worker icon. Please try again.');
    },
  });
};
