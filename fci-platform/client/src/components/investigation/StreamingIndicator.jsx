export default function StreamingIndicator() {
  return (
    <div className="px-5 py-2 shrink-0">
      <div className="max-w-4xl mx-auto flex justify-start">
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
          </div>
        </div>
      </div>
    </div>
  );
}
