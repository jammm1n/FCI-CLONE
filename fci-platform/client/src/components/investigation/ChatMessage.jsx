import MarkdownRenderer from '../shared/MarkdownRenderer';
import { formatTimestamp } from '../../utils/formatters';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const toolsUsed = message.tools_used || [];
  const isStreaming = message.isStreaming;

  return (
    <div className={`${isUser ? 'flex justify-end' : ''} animate-fade-in-up`}>
      <div
        className={`px-5 py-4 ${
          isUser
            ? 'max-w-[75%] bg-gold-500/10 border border-gold-500/20 rounded-2xl rounded-br-md'
            : 'bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-2xl rounded-bl-md shadow-soft-sm'
        }`}
      >
        {/* Role label + timestamp */}
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-sm font-semibold ${
            isUser ? 'text-gold-600 dark:text-gold-500' : 'text-surface-600 dark:text-surface-400'
          }`}>
            {isUser ? 'You' : 'AI Assistant'}
          </span>
          <span className="text-xs text-surface-400">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>

        {/* Image thumbnails (user messages) */}
        {isUser && message.images && message.images.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {message.images.map((img, i) => (
              <div key={i} className="w-24 h-24 rounded-xl border-2 border-gold-200 dark:border-gold-800 overflow-hidden bg-surface-100 dark:bg-surface-900 hover:scale-105 transition-transform cursor-pointer">
                {img.preview ? (
                  <img src={img.preview} alt={`Attachment ${i + 1}`} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-xs text-surface-500">Image</div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Content */}
        {isUser ? (
          <p className="text-base text-surface-800 dark:text-surface-200 leading-relaxed whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="text-base leading-relaxed">
            <MarkdownRenderer content={message.content} />
            {isStreaming && (
              <span className="animate-blink text-gold-500 ml-0.5">&#9612;</span>
            )}
          </div>
        )}

        {/* Tools used footer */}
        {toolsUsed.length > 0 && (
          <div className="mt-3 pt-3 border-t border-surface-100 dark:border-surface-700">
            <span className="text-sm text-surface-500">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5 inline mr-1 opacity-60">
                <path d="M2 4a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V4zm2-.5a.5.5 0 00-.5.5v8a.5.5 0 00.5.5h8a.5.5 0 00.5-.5V4a.5.5 0 00-.5-.5H4z" />
              </svg>
              Referenced:{' '}
            </span>
            {toolsUsed.map((t, i) => (
              <span key={i} className="text-sm text-gold-600 dark:text-gold-400 font-medium">
                {t.document_title}
                {i < toolsUsed.length - 1 ? ', ' : ''}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
