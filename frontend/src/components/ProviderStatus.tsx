import React from 'react';
import { ProviderStatus as ProviderStatusType } from '../api/client';

interface Props {
  status: ProviderStatusType | null;
  loading: boolean;
}

const providerLabels: Record<string, string> = {
  anthropic: 'Anthropic Claude',
  ollama_vision: 'Ollama Vision',
  ollama_ocr: 'Ollama OCR',
};

const providerIcons: Record<string, string> = {
  anthropic: '🤖',
  ollama_vision: '👁️',
  ollama_ocr: '📝',
};

export function ProviderStatus({ status, loading }: Props) {
  if (loading) {
    return (
      <div className="provider-status loading">
        <span className="provider-icon">⏳</span>
        <span className="provider-text">Loading provider status...</span>
      </div>
    );
  }

  if (!status) {
    return null;
  }

  const providerName = providerLabels[status.configured_provider] || status.configured_provider;
  const icon = providerIcons[status.configured_provider] || '🔧';
  const modelInfo = status.configured_provider === 'anthropic'
    ? 'Claude API'
    : status.configured_provider === 'ollama_ocr'
    ? `${status.config.ocr_engine} + ${status.config.ollama_text_model}`
    : status.config.ollama_vision_model;

  return (
    <div className={`provider-status ${status.available ? 'available' : 'unavailable'}`}>
      <span className="provider-icon">{icon}</span>
      <div className="provider-info">
        <span className="provider-name">{providerName}</span>
        <span className="provider-model">{modelInfo}</span>
      </div>
      <span className={`provider-badge ${status.available ? 'success' : 'error'}`}>
        {status.available ? '● Active' : '● Unavailable'}
      </span>
    </div>
  );
}
