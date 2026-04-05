import { logger } from '@/lib/logger';
import { create } from 'zustand';

interface DocumentModalState {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

export const useDocumentModalStore = create<DocumentModalState>((set) => ({
  isOpen: false,
  setIsOpen: (isOpen) => {
    logger.log('Document modal store - setting isOpen to:', isOpen);
    set({ isOpen });
  },
})); 