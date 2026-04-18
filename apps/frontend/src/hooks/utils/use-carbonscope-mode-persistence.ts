'use client';

import { useCallback } from 'react';
import { useCarbonScopeModesStore } from '@/stores/carbonscope-modes-store';

// Hook that provides methods to manage CarbonScope mode selections
export function useCarbonScopeModePersistence() {
  const store = useCarbonScopeModesStore();
  
  const setSelectedMode = useCallback((mode: string | null) => {
    store.setSelectedMode(mode);
  }, [store]);
  
  const setSelectedCharts = useCallback((charts: string[]) => {
    store.setSelectedCharts(charts);
  }, [store]);
  
  const setSelectedOutputFormat = useCallback((format: string | null) => {
    store.setSelectedOutputFormat(format);
  }, [store]);
  
  const setSelectedTemplate = useCallback((template: string | null) => {
    store.setSelectedTemplate(template);
  }, [store]);
  
  const setSelectedDocsType = useCallback((type: string | null) => {
    store.setSelectedDocsType(type);
  }, [store]);
  
  const setSelectedImageStyle = useCallback((style: string | null) => {
    store.setSelectedImageStyle(style);
  }, [store]);
  
  const setSelectedCanvasAction = useCallback((action: string | null) => {
    store.setSelectedCanvasAction(action);
  }, [store]);
  
  const setSelectedVideoStyle = useCallback((style: string | null) => {
    store.setSelectedVideoStyle(style);
  }, [store]);
  
  
  return {
    // State
    selectedMode: store.selectedMode,
    selectedCharts: store.selectedCharts,
    selectedOutputFormat: store.selectedOutputFormat,
    selectedTemplate: store.selectedTemplate,
    selectedDocsType: store.selectedDocsType,
    selectedImageStyle: store.selectedImageStyle,
    selectedCanvasAction: store.selectedCanvasAction,
    selectedVideoStyle: store.selectedVideoStyle,
    // Actions
    setSelectedMode,
    setSelectedCharts,
    setSelectedOutputFormat,
    setSelectedTemplate,
    setSelectedDocsType,
    setSelectedImageStyle,
    setSelectedCanvasAction,
    setSelectedVideoStyle,
  };
}
