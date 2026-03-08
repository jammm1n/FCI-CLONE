export default function StreamingIndicator({ onStop }) {
  return (
    <div className="py-2 shrink-0" style={{ paddingLeft: '5%', paddingRight: '5%' }}>
      <div className="flex justify-start">
        <div className="max-w-[200px] bg-surface-50 dark:bg-surface-800 rounded-2xl rounded-bl-md px-5 py-4 border border-surface-200 dark:border-surface-700 shadow-soft-sm animate-fade-in-up relative overflow-hidden">
          {/* Gold shimmer overlay */}
          <div className="absolute inset-0 animate-gold-shimmer pointer-events-none" />

          <div className="relative flex items-center gap-3">
            <div className="flex gap-1.5">
              <div className="w-2 h-2 rounded-full bg-gold-500 animate-pulse-subtle" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 rounded-full bg-gold-500 animate-pulse-subtle" style={{ animationDelay: '200ms' }} />
              <div className="w-2 h-2 rounded-full bg-gold-500 animate-pulse-subtle" style={{ animationDelay: '400ms' }} />
            </div>
            <span className="text-sm text-gold-500/70">Analyzing...</span>
            {onStop && (
              <button
                onClick={onStop}
                className="ml-1 w-5 h-5 rounded flex items-center justify-center bg-surface-200 dark:bg-surface-700 hover:bg-red-500/20 text-surface-500 hover:text-red-400 transition-colors"
                title="Stop"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3 h-3">
                  <rect x="3" y="3" width="10" height="10" rx="1" />
                </svg>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
