import { useState } from 'react';

export default function QCPasteModal({ onSubmit, onCancel, loading }) {
  const [text, setText] = useState('');

  function handleSubmit() {
    if (!text.trim()) return;
    onSubmit(text.trim());
  }

  function handleKeyDown(e) {
    if (e.key === 'Escape' && !loading) {
      onCancel();
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in"
      onClick={!loading ? onCancel : undefined}
      onKeyDown={handleKeyDown}
    >
      <div
        className="w-full max-w-2xl mx-4 bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-2xl shadow-2xl animate-fade-in-up"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-surface-200 dark:border-surface-700">
          <h2 className="text-lg font-semibold text-surface-800 dark:text-surface-100">
            QC Check
          </h2>
          <p className="text-sm text-surface-500 dark:text-surface-400 mt-1">
            Paste your case file from HaoDesk for quality control review.
          </p>
        </div>

        {/* Textarea */}
        <div className="p-6">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={loading}
            placeholder="Paste case text here..."
            rows={12}
            className="w-full px-4 py-3 text-sm bg-surface-100 dark:bg-surface-900 text-surface-900 dark:text-surface-100 placeholder-surface-400 border border-surface-200 dark:border-surface-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-gold-500/30 focus:border-gold-500 resize-y disabled:opacity-50 font-mono"
            autoFocus
          />
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-surface-200 dark:border-surface-700 flex items-center justify-end gap-3">
          <button
            onClick={onCancel}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-surface-600 dark:text-surface-400 hover:text-surface-800 dark:hover:text-surface-200 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading || !text.trim()}
            className="px-5 py-2 text-sm font-semibold rounded-lg bg-gradient-to-r from-gold-500 to-gold-400 text-surface-950 disabled:from-surface-300 disabled:to-surface-400 dark:disabled:from-surface-700 dark:disabled:to-surface-600 disabled:text-surface-500 flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-surface-950/30 border-t-surface-950 rounded-full animate-spin" />
                Generating summary...
              </>
            ) : (
              'Submit for QC'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
