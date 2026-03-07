const MAX_CONTEXT = 200_000;

function formatK(n) {
  if (n == null) return '—';
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return String(n);
}

export default function TokenUsageDisplay({ tokenUsage }) {
  if (!tokenUsage) return null;

  const { input_tokens, output_tokens, cache_read_input_tokens, cache_creation_input_tokens } = tokenUsage;
  const cacheRead = cache_read_input_tokens || 0;
  const cacheCreated = cache_creation_input_tokens || 0;
  const totalInput = (input_tokens || 0) + cacheRead + cacheCreated;
  const pct = Math.min(100, (totalInput / MAX_CONTEXT) * 100);

  return (
    <div className="flex items-center gap-3 text-xs text-surface-500 dark:text-surface-400 font-mono select-none">
      {/* Context bar */}
      <div className="flex items-center gap-1.5">
        <span>ctx</span>
        <div className="w-20 h-1.5 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              pct > 80 ? 'bg-red-500' : pct > 60 ? 'bg-gold-500' : 'bg-emerald-500'
            }`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <span>{formatK(totalInput)}<span className="text-surface-400 dark:text-surface-500">/{formatK(MAX_CONTEXT)}</span></span>
      </div>

      <span className="text-surface-300 dark:text-surface-600">|</span>

      {/* Output tokens */}
      <span>out {formatK(output_tokens)}</span>

      {/* Cache info — only show if there's cache activity */}
      {(cacheRead > 0 || cacheCreated > 0) && (
        <>
          <span className="text-surface-300 dark:text-surface-600">|</span>
          {cacheRead > 0 && <span className="text-emerald-600 dark:text-emerald-400">cache {formatK(cacheRead)}</span>}
          {cacheCreated > 0 && <span className="text-gold-600 dark:text-gold-400">+new {formatK(cacheCreated)}</span>}
        </>
      )}
    </div>
  );
}
