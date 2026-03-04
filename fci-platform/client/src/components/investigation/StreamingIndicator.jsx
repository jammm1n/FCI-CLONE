export default function StreamingIndicator() {
  return (
    <div className="px-4 py-2 shrink-0">
      <div className="flex items-center gap-2 text-sm text-surface-400">
        <div className="flex gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="w-1.5 h-1.5 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="w-1.5 h-1.5 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
        <span>AI is thinking...</span>
      </div>
    </div>
  );
}
