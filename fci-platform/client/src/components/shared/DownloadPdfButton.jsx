import { useState, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { exportPdf } from '../../services/api';

const ICON_CLASS =
  'w-8 h-8 rounded-lg flex items-center justify-center transition-colors duration-200';

export default function DownloadPdfButton({ conversationId, disabled }) {
  // 'idle' | 'generating' | 'done' | 'error'
  const [state, setState] = useState('idle');
  const { token } = useAuth();

  const handleClick = useCallback(async () => {
    if (state === 'generating' || !conversationId) return;
    setState('generating');

    try {
      await exportPdf(token, conversationId);
      setState('done');
      setTimeout(() => setState('idle'), 2000);
    } catch {
      setState('error');
      setTimeout(() => setState('idle'), 3000);
    }
  }, [token, conversationId, state]);

  const isDisabled = disabled || !conversationId || state === 'generating';

  const title =
    state === 'generating'
      ? 'Generating PDF...'
      : state === 'done'
        ? 'PDF downloaded'
        : state === 'error'
          ? 'PDF export failed'
          : 'Download transcript as PDF';

  const label =
    state === 'generating'
      ? 'Exporting...'
      : state === 'done'
        ? 'Exported'
        : state === 'error'
          ? 'Export failed'
          : 'Export transcript';

  return (
    <button
      onClick={handleClick}
      disabled={isDisabled}
      title={title}
      className={`flex items-center gap-1.5 px-2.5 h-8 rounded-lg transition-colors duration-200 ${
        isDisabled
          ? 'text-surface-400 dark:text-surface-600 cursor-not-allowed'
          : state === 'error'
            ? 'text-red-500'
            : state === 'done'
              ? 'text-emerald-500'
              : 'text-surface-500 dark:text-surface-400 hover:text-gold-500 dark:hover:text-gold-500 hover:bg-surface-100 dark:hover:bg-surface-700'
      }`}
    >
      {state === 'generating' ? (
        <svg className="w-3.5 h-3.5 animate-spin text-gold-500 shrink-0" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="31.4 31.4" strokeLinecap="round" />
        </svg>
      ) : state === 'done' ? (
        <svg className="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      ) : state === 'error' ? (
        <svg className="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      ) : (
        <svg className="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
      )}
      <span className="text-xs font-medium">{label}</span>
    </button>
  );
}
