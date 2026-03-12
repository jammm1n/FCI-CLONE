import { useState, useEffect, useCallback, useRef } from 'react';
import MarkdownRenderer from '../shared/MarkdownRenderer';

const POPOUT_TABS = new Set(['elliptic_raw']);

function FitToScreenModal({ content, onClose }) {
  const containerRef = useRef(null);
  const contentRef = useRef(null);
  const [scale, setScale] = useState(1);

  // Measure content and compute scale to fit viewport
  useEffect(() => {
    const container = containerRef.current;
    const inner = contentRef.current;
    if (!container || !inner) return;

    // Let content render at natural size first
    setScale(1);

    const frame = requestAnimationFrame(() => {
      const availableHeight = container.clientHeight;
      const naturalHeight = inner.scrollHeight;

      if (naturalHeight > availableHeight) {
        const fitted = availableHeight / naturalHeight;
        // Clamp to a minimum of 0.25 — below that it's unreadable
        setScale(Math.max(0.25, fitted));
      } else {
        setScale(1);
      }
    });

    return () => cancelAnimationFrame(frame);
  }, [content]);

  // Close on Escape
  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="relative w-[96vw] h-[96vh] bg-surface-50 dark:bg-surface-900 rounded-lg shadow-2xl border border-surface-200 dark:border-surface-700 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-2 border-b border-surface-200 dark:border-surface-700 shrink-0">
          <h3 className="text-xs font-semibold text-surface-700 dark:text-surface-200">
            Elliptic Screening Results — Fit to Screen
          </h3>
          <div className="flex items-center gap-3">
            <span className="text-[10px] text-surface-400">
              {scale < 1 ? `${Math.round(scale * 100)}%` : '100%'}
            </span>
            <button
              onClick={onClose}
              className="p-1 rounded-md hover:bg-surface-200 dark:hover:bg-surface-700 text-surface-500 dark:text-surface-400 hover:text-surface-700 dark:hover:text-surface-200 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        {/* Content area — no overflow scroll, content is scaled to fit */}
        <div ref={containerRef} className="flex-1 overflow-hidden p-4">
          <div
            ref={contentRef}
            style={{
              transform: `scale(${scale})`,
              transformOrigin: 'top left',
              width: scale < 1 ? `${100 / scale}%` : '100%',
            }}
          >
            <MarkdownRenderer content={content} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default function CaseDataPanel({ content, activeTab }) {
  const [modalOpen, setModalOpen] = useState(false);

  const showPopout = POPOUT_TABS.has(activeTab) && !!content;

  // Close modal when switching tabs
  useEffect(() => {
    setModalOpen(false);
  }, [activeTab]);

  if (!content) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-10 h-10 mx-auto mb-2 text-surface-300 dark:text-surface-600 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
          <p className="text-sm text-surface-400">Select a data tab to view case information.</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="flex-1 overflow-y-auto custom-scrollbar p-6 bg-surface-100 dark:bg-surface-850 relative grain-texture" style={{ scrollBehavior: 'smooth' }}>
        {showPopout && (
          <button
            onClick={() => setModalOpen(true)}
            title="Fit to screen (for screenshots)"
            className="absolute top-3 right-3 z-20 p-1.5 rounded-md bg-surface-200/80 dark:bg-surface-700/80 hover:bg-surface-300 dark:hover:bg-surface-600 text-surface-500 dark:text-surface-400 hover:text-surface-700 dark:hover:text-surface-200 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9m11.25-5.25v4.5m0-4.5h-4.5m4.5 0L15 9m-11.25 11.25v-4.5m0 4.5h4.5m-4.5 0L9 15m11.25 5.25v-4.5m0 4.5h-4.5m4.5 0L15 15" />
            </svg>
          </button>
        )}
        <div key={activeTab} className="relative z-10 animate-fade-in">
          <MarkdownRenderer content={content} />
        </div>
      </div>

      {modalOpen && (
        <FitToScreenModal
          content={content}
          onClose={() => setModalOpen(false)}
        />
      )}
    </>
  );
}
